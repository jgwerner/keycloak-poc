import json, os, urllib

from dotenv import load_dotenv

from tornado.auth import OAuth2Mixin
from tornado import gen, web
from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import LogoutHandler
from jupyterhub.utils import url_path_join

from oauthenticator.oauth2 import OAuthLoginHandler, OAuthenticator


load_dotenv()


oidc_client_id = os.getenv('OIDC_CLIENT_ID')    
oidc_server_host = os.getenv('OIDC_SERVER')


class KeycloakMixin(OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = "{}/auth/realms/{}/protocol/openid-connect/auth".format(oidc_server_host, oidc_client_id)
    _OAUTH_ACCESS_TOKEN_URL = "{}/auth/realms/{}/protocol/openid-connect/token".format(oidc_server_host, oidc_client_id)
    _OAUTH_LOGOUT_URL = "{}/auth/realms/{}/protocol/openid-connect/logout".format(oidc_server_host, oidc_client_id)
    _OAUTH_USERINFO_URL = "{}/auth/realms/{}/protocol/openid-connect/userinfo".format(oidc_server_host, oidc_client_id)

class KeycloakLoginHandler(OAuthLoginHandler, KeycloakMixin):
    pass

class KeycloakLogoutHandler(LogoutHandler, KeycloakMixin):
    def get(self):
        params = dict(
            redirect_uri="%s://%s%slogout" % (
                self.request.protocol, self.request.host,
                self.hub.server.base_url)
        )
        logout_url = KeycloakMixin._OAUTH_LOGOUT_URL
        logout_url = url_concat(logout_url, params)
        self.redirect(logout_url, permanent=False)

class KeycloakOAuthenticator(OAuthenticator, KeycloakMixin):
    login_service = "OIDC"
    login_handler = KeycloakLoginHandler

    authorize_url = "{}/auth/realms/{}/protocol/openid-connect/auth".format(oidc_server_host, oidc_client_id)
    access_token_url = "{}/auth/realms/{}/protocol/openid-connect/token".format(oidc_server_host, oidc_client_id)
    oauth_logout_url = "{}/auth/realms/{}/protocol/openid-connect/logout".format(oidc_server_host, oidc_client_id)
    oauth_userinfo_url = "{}/auth/realms/{}/protocol/openid-connect/userinfo".format(oidc_server_host, oidc_client_id)

    def check_whitelist(self, username, authentication=None):
        self.log.info('Checking whilelist for username: %r', username)
        return True

    def logout_url(self, base_url):
        return url_path_join(base_url, 'oauth_logout')

    def get_handlers(self, app):
        handlers = OAuthenticator.get_handlers(self, app)
        handlers.extend([(r'/oauth_logout', KeycloakLogoutHandler)])
        return handlers

    @gen.coroutine
    def authenticate(self, handler, data=None):
        code = handler.get_argument("code", False)
        self.log.info('code: %s', code)
        if not code:
            raise web.HTTPError(400, "oauth callback made without a token")
        http_client = AsyncHTTPClient()
        params = dict(
            grant_type='authorization_code',
            code=code,
            redirect_uri=self.get_callback_url(handler),
        )
        token_url = KeycloakMixin._OAUTH_ACCESS_TOKEN_URL
        token_req = HTTPRequest(
            token_url,
            method="POST",
            headers={
                "Accept": "application/json",
                 "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            },
            auth_username = self.client_id,
            auth_password = self.client_secret,
            body = urllib.parse.urlencode(params).encode('utf-8'),
            )
        token_resp = yield http_client.fetch(token_req)
        token_resp_json = json.loads(token_resp.body.decode('utf8', 'replace'))
        access_token = token_resp_json['access_token']
        if not access_token:
            raise web.HTTPError(400, "failed to get access token")
        self.log.info('oauth token: %r', access_token)
        user_info_url = KeycloakMixin._OAUTH_USERINFO_URL
        user_info_req = HTTPRequest(
            user_info_url,
            method="GET",
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer %s" % access_token
                },
            )
        user_info_res = yield http_client.fetch(user_info_req)
        self.log.info('user_info_res: %r', user_info_res)
        user_info_res_json = json.loads(user_info_res.body.decode('utf8', 'replace'))
        self.log.info('user_info_res_json: %r', user_info_res_json)
        return {
            'name': user_info_res_json['preferred_username'],
            'auth_state': {
                'upstream_token': user_info_res_json,
            },
        }

# --- Proxy ---
c.ConfigurableHTTPProxy.api_url = 'http://jupyterhub:8081'

# --- Common ---
c.JupyterHub.base_url = '/jupyter'
c.JupyterHub.port = 8080
c.JupyterHub.cookie_secret = bytes.fromhex('c336ff8bc0f477928cfc73454821ee11182e90a49de57f81e0919e66851349c6')
c.ConfigurableHTTPProxy.auth_token = '0bc02bede919e99a26de1e2a7a5aadfaf6228de836ec39a05a6c6942831d8fe5'
c.JupyterHub.confirm_no_ssl = True
c.Authenticator.enable_auth_state = True

# --- Authenticator ---
# Set the authenticator
c.JupyterHub.authenticator_class = KeycloakOAuthenticator

# Accept admins and users
c.Authenticator.admin_users = {'admin'}
c.Authenticator.auto_login = True
c.Authenticator.allowed_users = {'greg', 'abhi', 'greg@example.com'}

# Verify TLS certificates.
if os.environ.get('OAUTH2_TLS_VERIFY') == 'True':
    c.OAuthenticator.tls_verify = True
else:
    c.OAuthenticator.tls_verify = False

c.KeycloakOAuthenticator.client_id = oidc_client_id
c.KeycloakOAuthenticator.client_secret = os.getenv('OIDC_SECRET')
c.Authenticator.auto_login = True

# --- Spawner ---
c.Spawner.debug = True
c.Spawner.default_url = '/lab'
c.Spawner.args = ['--NotebookApp.tornado_settings={"headers":{"Content-Security-Policy": "frame-ancestors *"}}']   
c.JupyterHub.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}
c.NotebookApp.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}

def docker_spawner(c):
    c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
    c.DockerSpawner.image = 'jupyterhub/singleuser:1.2'
    c.DockerSpawner.default_url = '/lab'
    c.DockerSpawner.remove_containers = True
    from jupyter_client.localinterfaces import public_ips
    c.JupyterHub.hub_ip = public_ips()[0]

docker_spawner(c)
