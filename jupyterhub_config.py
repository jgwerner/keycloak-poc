""" Configuration file for jupyterhub. """
import os

from dotenv import load_dotenv

from oauthenticator.generic import GenericOAuthenticator


load_dotenv()


# Set log level
c.Application.log_level = 'DEBUG'

# Set port and IP
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 8000

# Header settings for iFrame and SameSite
c.JupyterHub.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}

c.JupyterHub.allow_root = True
c.JupyterHub.allow_origin = '*'

# Set the authenticator
c.JupyterHub.authenticator_class = GenericOAuthenticator

c.Authenticator.admin_users = {'admin'}
c.Authenticator.auto_login = True
c.Authenticator.allowed_users = {'greg', 'abhi',}

# Verify TLS certificates.
if os.environ.get('OAUTH2_TLS_VERIFY') == 'True':
    c.OAuthenticator.tls_verify = True
else:
    c.OAuthenticator.tls_verify = False

# OAuthenticator settings for OAuth2
c.OAuthenticator.client_id = os.environ.get('OAUTH_CLIENT_ID')
c.OAuthenticator.client_secret = os.environ.get('OAUTH_CLIENT_SECRET')
c.OAuthenticator.oauth_callback_url = os.environ.get('OAUTH_CALLBACK_URL') or 'http://localhost:8000/hub/oauth_callback'
c.OAuthenticator.authorize_url = os.environ.get('OAUTH2_AUTHORIZE_URL') or f'http://localhost:8080/auth/realms/illumidesk-realm/protocol/openid-connect/auth'
c.OAuthenticator.token_url = os.environ.get('OAUTH2_TOKEN_URL') or f'http://localhost:8080/auth/realms/illumidesk-realm/protocol/openid-connect/token'
c.OAuthenticator.enable_auth_state = True

# Login service name
c.GenericOAuthenticator.login_service = os.environ.get('GENERICAUTH_LOGIN_SERVICE_NAME') or 'Keycloak'
# TODO: clarify scopes
# c.KeycloakAuthenticator.scope = ['email', 'read_api', 'read_user', 'openid', 'profile']
c.GenericOAuthenticator.userdata_url = os.environ.get('GENERICAUTH_USERDATA_URL') or 'http://localhost:8080/auth/realms/illumidesk-realm/protocol/openid-connect/userinfo'
c.GenericOAuthenticator.userdata_method = os.environ.get('GENERICAUTH_USERDATA_METHOD') or 'GET'
userdata_params = {
    os.environ.get('GENERICAUTH_USERNAME_PARAMS_KEY') or 'state' : os.environ.get('GENERICAUTH_USERNAME_PARAMS_VALUE') or 'state' }
c.GenericOAuthenticator.userdata_params = userdata_params
c.GenericOAuthenticator.username_key = os.environ.get('GENERICAUTH_USERNAME_KEY') or 'sub'

# Set Keycloak logout url
c.GenericOAuthenticator.keycloak_logout_url = os.environ.get('KEYCLOAK_LOGOUT_URL') or 'http://localhost:8080/auth/realms/illumidesk-realm/protocol/openid-connect/logout'