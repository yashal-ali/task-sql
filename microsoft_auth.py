import msal
import requests
import streamlit as st
from urllib.parse import urlencode

class MicrosoftAuth:
    def __init__(self):
        self.client_id = "91355889-9814-4a6c-8bbe-29942e67e5b8"
        self.tenant_id = "3953756b-80d0-4171-a6b0-6e36c763297f"
        self.client_secret = "m7Y8Q~5L1fV.wtyzpfSe5VeFQv9fIoCixf1n3c9s"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["User.Read"]  # Simplified scope
        self.graph_endpoint = "https://graph.microsoft.com/v1.0/me"
        
    def get_redirect_uri(self):
        """Get the redirect URI dynamically"""
        # For local development
        if 'localhost' in st.get_option('browser.serverAddress') or st.get_option('browser.serverAddress') == '0.0.0.0':
            return "http://localhost:8501"
        # For deployed app - update with your actual domain
        return "https://your-app-domain.streamlit.app"
    
    def get_auth_url(self):
        """Generate Microsoft OAuth authorization URL"""
        try:
            redirect_uri = self.get_redirect_uri()
            
            # Build authorization URL manually for better control
            params = {
                'client_id': self.client_id,
                'response_type': 'code',
                'redirect_uri': redirect_uri,
                'response_mode': 'query',
                'scope': 'openid profile email User.Read',
                'state': 'taskflow_auth'  # Add state for security
            }
            
            auth_url = f"{self.authority}/oauth2/v2.0/authorize?{urlencode(params)}"
            return auth_url
            
        except Exception as e:
            print(f"Error generating auth URL: {e}")
            return None
    
    def get_token_from_code(self, code):
        """Exchange authorization code for access token"""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_by_authorization_code(
                code,
                scopes=self.scope,
                redirect_uri=self.get_redirect_uri()
            )
            
            if "error" in result:
                print(f"Token acquisition error: {result.get('error')}")
                print(f"Error description: {result.get('error_description')}")
                return None
            
            return result
            
        except Exception as e:
            print(f"Error acquiring token: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Fetch user information from Microsoft Graph API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.graph_endpoint, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                    'displayName': user_data.get('displayName'),
                    'givenName': user_data.get('givenName'),
                    'surname': user_data.get('surname'),
                    'id': user_data.get('id')
                }
            else:
                print(f"Graph API error: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return None

# Create global instance
ms_auth = MicrosoftAuth()