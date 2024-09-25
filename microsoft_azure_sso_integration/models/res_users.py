import json
import logging
import requests

from odoo import api, models, _
from odoo.http import request
from odoo.addons.auth_signup.models.res_users import SignupError

_logger = logging.getLogger(__name__)

try:
    import jwt
except ImportError:
    _logger.warning("Login with Microsoft account won't be available. Please install PyJWT python library.")
    jwt = None

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _auth_oauth_rpc(self, endpoint, access_token):
        """ Pass the response of sign in """
        _logger.info(f"Calling OAuth endpoint: {endpoint} with access token.")
        res = super()._auth_oauth_rpc(endpoint, access_token)
        _logger.info(f"OAuth endpoint response: {res}")
        if endpoint:
            return requests.get(endpoint, params={'access_token': access_token}).json()
        return res
    
    @api.model
    def _auth_oauth_code_validate(self, provider, code):
        _logger.info(f"Validating OAuth code for provider: {provider} with code: {code}")
        auth_oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation_data = super(ResUsers, self)._auth_oauth_code_validate(provider, code)
        
        _logger.info(f"Validation data received: {validation_data}")

        # Search for the user based on the OAuth UID
        user_oauth = self.search([('oauth_uid', '=', validation_data.get('user_id'))])
        _logger.info(f"User search result for OAuth UID: {validation_data.get('user_id')}, found: {user_oauth}")
        
        if not user_oauth:
            # If user is not found, raise an error instead of creating a new user
            _logger.warning(f"Access Denied: No user found with OAuth UID: {validation_data.get('user_id')}")
            raise AccessDenied(_("Access Denied: User is not registered in Odoo. Please contact your administrator."))
        
        _logger.info(f"User {user_oauth} found, proceeding with authentication.")
        return validation_data

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        _logger.info(f"Signing in user with provider: {provider} and validation data: {validation}")
        user = self.search([('login', '=', str(validation.get('email')))])
        
        if not user:
            _logger.info(f"No user found with email {validation.get('email')}, creating new user.")
            user = self.create({
                'login': str(validation.get('email')),
                'name': str(validation.get('name'))
            })
        
        _logger.info(f"Updating user OAuth info for user: {user}")
        user.write({
            'oauth_provider_id': provider,
            'oauth_uid': validation['user_id'],
            'oauth_access_token': params['access_token'],
        })

        try:
            oauth_uid = validation['user_id']
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                _logger.warning(f"Access Denied: No OAuth user found with UID: {oauth_uid}")
                raise Exception("Access Denied")
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            _logger.info(f"User {oauth_user.login} successfully signed in with OAuth.")
            return oauth_user.login
        except (Exception, Exception) as e:
            _logger.error(f"Error during OAuth sign-in: {e}")
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except SignupError as e:
                _logger.error(f"Signup error: {e}")
                raise Exception("Access Denied")
        return super(ResUsers, self)._auth_oauth_signin(provider, validation, params)

    @api.model
    def auth_oauth(self, provider, params):
        _logger.info(f"Starting OAuth authentication for provider: {provider} with params: {params}")
        if params.get('code'):
            validation = self._auth_oauth_code_validate(provider, params['code'])
            access_token = validation.pop('access_token')
            params['access_token'] = access_token
        else:
            access_token = params.get('access_token')
            validation = self._auth_oauth_validate(provider, access_token)
        
        _logger.info(f"Validation result: {validation}")

        if not validation.get('user_id'):
            _logger.warning(f"Validation failed: No user_id in validation data: {validation}")
            if validation.get('id'):
                validation['user_id'] = validation['id']
            elif validation.get('oid'):
                validation['user_id'] = validation['oid']
            else:
                raise Exception("Access Denied")
        
        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            _logger.warning(f"Access Denied: Unable to sign in user with provider {provider}.")
            raise Exception("Access Denied")
        
        _logger.info(f"OAuth authentication successful for user: {login}")
        if provider and params:
            return self.env.cr.dbname, login, access_token
        return super(ResUsers, self).auth_oauth(provider, params)
