"""
GitLab API client for managing CI/CD variables (secrets).

This module provides a client interface for interacting with GitLab's CI/CD Variables API.
It handles all CRUD operations for managing environment variables/secrets in GitLab projects.
The client abstracts away the HTTP details and provides a simple Python interface.

Example:
    from config import Config
    from gitlab_client import GitLabClient
    
    config = Config()
    config.validate()
    client = GitLabClient(config)
    
    # Create a new variable
    variable = client.create_variable('API_KEY', 'secret123', protected=True)
    
    # List all variables
    variables = client.list_variables()
"""
import requests
from typing import List, Dict, Optional, Any
from urllib.parse import quote
from config import Config


class GitLabClient:
    """
    Client for interacting with GitLab CI/CD Variables API.
    
    This class provides methods to create, read, update, and delete CI/CD variables
    (secrets) in a GitLab project. It handles authentication and all HTTP details
    internally.
    
    Attributes:
        config (Config): Configuration object containing API credentials
        base_url (str): Base URL for GitLab API v4 endpoints
        headers (dict): HTTP headers including authentication token
    
    Example:
        >>> config = Config()
        >>> config.validate()
        >>> client = GitLabClient(config)
        >>> variables = client.list_variables()
    """
    
    def __init__(self, config: Config):
        """
        Initialize the GitLab API client.
        
        Args:
            config (Config): Configuration object with GitLab credentials and project ID
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config = config
        
        # Construct the base API URL (GitLab API v4)
        # Format: https://gitlab.com/api/v4
        self.base_url = f"{config.gitlab_url}/api/v4"
        
        # Set up HTTP headers for authentication
        # PRIVATE-TOKEN is GitLab's authentication method for personal access tokens
        self.headers = {
            'PRIVATE-TOKEN': config.gitlab_token,
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request to GitLab API.
        
        Internal method that handles all HTTP requests to the GitLab API. It adds
        authentication headers and handles errors uniformly.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path (e.g., 'projects/123/variables')
            **kwargs: Additional arguments to pass to requests.request()
            
        Returns:
            requests.Response: The HTTP response object
            
        Raises:
            requests.exceptions.HTTPError: If the API returns an error status code
            
        Example:
            >>> response = self._make_request('GET', 'projects/123/variables')
            >>> data = response.json()
        """
        # Construct the full URL
        url = f"{self.base_url}/{endpoint}"
        
        # Make the HTTP request with authentication headers
        response = requests.request(method, url, headers=self.headers, **kwargs)
        
        # Raise an exception for HTTP error status codes (4xx, 5xx)
        response.raise_for_status()
        
        return response
    
    def list_variables(self) -> List[Dict[str, Any]]:
        """
        List all CI/CD variables for the project.
        
        Retrieves all environment variables/secrets configured for the GitLab project.
        These are the variables that can be used in CI/CD pipelines.
        
        Note: GitLab API uses pagination (20 items per page by default). This method
        automatically fetches all pages to return the complete list of variables.
        
        Returns:
            List[Dict[str, Any]]: List of variable dictionaries, each containing:
                - key: Variable name
                - value: Variable value
                - protected: Whether variable is only available on protected branches
                - masked: Whether variable is masked in job logs
                - raw: Whether variable value is expanded
                - environment_scope: Environment scope (default: '*')
        
        Raises:
            requests.exceptions.HTTPError: If API request fails
            
        Example:
            >>> variables = client.list_variables()
            >>> print(f"Found {len(variables)} variables")
        """
        # Initialize pagination variables
        all_variables = []
        page = 1
        per_page = 100  # Maximum allowed by GitLab API (default is 20)
        
        # Loop through all pages to fetch complete list
        while True:
            # GET /projects/:id/variables with pagination parameters
            # Using per_page=100 (max allowed) minimizes the number of API requests needed
            response = self._make_request('GET', 
                f'projects/{self.config.project_id}/variables',
                params={'page': page, 'per_page': per_page})
            
            # Extract variables from current page
            page_variables = response.json()
            all_variables.extend(page_variables)
            
            # Check pagination headers to determine if more pages exist
            # GitLab returns X-Total-Pages header indicating total number of pages
            total_pages = response.headers.get('X-Total-Pages', '1')
            
            # Safely convert to integer
            try:
                total_pages = int(total_pages)
            except (ValueError, TypeError):
                # If header is missing or invalid, assume only one page
                total_pages = 1
            
            # Exit loop if we've retrieved all pages
            if page >= total_pages:
                break
            
            # Increment page number for next iteration
            page += 1
        
        # Return complete list of all variables across all pages
        return all_variables
    
    def get_variable(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific CI/CD variable by key.
        
        Retrieves detailed information about a single CI/CD variable including its
        value and configuration settings.
        
        Args:
            key (str): The variable key/name to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Variable dictionary if found, None if not found.
                Contains the same fields as list_variables() but for a single variable.
        
        Raises:
            requests.exceptions.HTTPError: If API request fails (except 404)
            
        Example:
            >>> variable = client.get_variable('DATABASE_URL')
            >>> if variable:
            ...     print(f"Value: {variable['value']}")
        """
        try:
            # GET /projects/:id/variables/:key
            # URL-encode the key to handle special characters safely
            encoded_key = quote(key, safe='')
            response = self._make_request('GET', 
                f'projects/{self.config.project_id}/variables/{encoded_key}')
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Return None if variable doesn't exist (404 Not Found)
            if e.response.status_code == 404:
                return None
            # Re-raise other HTTP errors
            raise
    
    def create_variable(self, key: str, value: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new CI/CD variable.
        
        Creates a new environment variable/secret in the GitLab project. Optional
        parameters can control how the variable behaves in CI/CD pipelines.
        
        Args:
            key (str): Variable key/name (required)
            value (str): Variable value (required)
            **kwargs: Additional optional parameters:
                - protected (bool): Only available on protected branches/tags
                - masked (bool): Mask variable value in job logs
                - raw (bool): Don't expand variable value
                - environment_scope (str): Limit to specific environment
            
        Returns:
            Dict[str, Any]: Created variable dictionary with all its properties
            
        Raises:
            requests.exceptions.HTTPError: If creation fails (e.g., variable already exists)
            
        Example:
            >>> var = client.create_variable('API_KEY', 'secret123', protected=True, masked=True)
            >>> print(f"Created: {var['key']}")
        """
        # Prepare the data payload for the API request
        data = {
            'key': key,
            'value': value,
            **kwargs  # Include any additional parameters (protected, masked, etc.)
        }
        
        # POST /projects/:id/variables
        response = self._make_request('POST', 
            f'projects/{self.config.project_id}/variables', 
            json=data)
        return response.json()
    
    def update_variable(self, key: str, value: str = None, **kwargs) -> Dict[str, Any]:
        """
        Update an existing CI/CD variable.
        
        Updates the value and/or properties of an existing CI/CD variable. Only
        the provided parameters will be updated.
        
        Args:
            key (str): Variable key/name to update (required)
            value (str, optional): New variable value
            **kwargs: Additional parameters to update:
                - protected (bool): Set protected status
                - masked (bool): Set masked status
                - raw (bool): Set raw status
                - environment_scope (str): Set environment scope
            
        Returns:
            Dict[str, Any]: Updated variable dictionary
            
        Raises:
            requests.exceptions.HTTPError: If update fails (e.g., variable not found)
            
        Example:
            >>> var = client.update_variable('API_KEY', 'new_secret', protected=False)
            >>> print(f"Updated: {var['key']}")
        """
        # Build the update payload
        data = {}
        
        # Only include value if it's explicitly provided
        if value is not None:
            data['value'] = value
        
        # Add any other parameters to update
        data.update(kwargs)
        
        # PUT /projects/:id/variables/:key
        # URL-encode the key to handle special characters safely
        encoded_key = quote(key, safe='')
        response = self._make_request('PUT', 
            f'projects/{self.config.project_id}/variables/{encoded_key}', 
            json=data)
        return response.json()
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get project information including name and ID.
        
        Retrieves basic project information from GitLab API.
        
        Returns:
            Dict[str, Any]: Project information including:
                - id: Project ID
                - name: Project name
                - path_with_namespace: Full path with namespace
                - web_url: Project URL
        
        Raises:
            requests.exceptions.HTTPError: If the API returns an error status code
            
        Example:
            >>> project = client.get_project_info()
            >>> print(f"Project: {project['name']} (ID: {project['id']})")
        """
        # GET /projects/:id
        response = self._make_request('GET', 
            f'projects/{self.config.project_id}')
        return response.json()
    
    def delete_variable(self, key: str) -> bool:
        """
        Delete a CI/CD variable.
        
        Permanently removes a CI/CD variable from the GitLab project. This action
        cannot be undone.
        
        Args:
            key (str): Variable key/name to delete
            
        Returns:
            bool: True if deletion succeeded, False if variable didn't exist
            
        Raises:
            requests.exceptions.HTTPError: If deletion fails (except 404)
            
        Example:
            >>> success = client.delete_variable('OLD_API_KEY')
            >>> if success:
            ...     print("Variable deleted")
        """
        try:
            # DELETE /projects/:id/variables/:key
            # URL-encode the key to handle special characters safely
            encoded_key = quote(key, safe='')
            self._make_request('DELETE', 
                f'projects/{self.config.project_id}/variables/{encoded_key}')
            return True
        except requests.exceptions.HTTPError as e:
            # Return False if variable doesn't exist (404 Not Found)
            if e.response.status_code == 404:
                return False
            # Re-raise other HTTP errors
            raise

