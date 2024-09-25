import json
import logging
import requests

from odoo import api, models, _
from odoo.http import request
from odoo.addons import base
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
        res = super()._auth_oauth_rpc(endpoint, access_token)
        if endpoint:
            return requests.get(endpoint, params={'access_token': access_token}).json()
        return res

    @api.model
    def _auth_oauth_code_validate(self, provider, code):
        """ Return the validation data corresponding to the access token """
        auth_oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        # AJUSTES FH
        redirect_uri = 'https://' + request.httprequest.host + '/auth_oauth/signin'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        token_info = requests.post(
            auth_oauth_provider.validation_endpoint,
            headers=headers,
            data={
                'client_id': auth_oauth_provider.client_id,
                'client_secret': auth_oauth_provider.client_secret_id,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri
            }
        ).json()

        if token_info.get("error"):
            raise Exception(token_info['error'])
        access_token = token_info.get('access_token')
        validation = {
            'access_token': access_token
        }
        if token_info.get('id_token'):
            if not jwt:
                raise Exception("Access Denied")
            #data = jwt.decode(token_info['id_token'], verify=False)
            data = jwt.decode(token_info['id_token'], options={"verify_signature": False}, algorithms=["RS256"])
        else:
            data = self._auth_oauth_rpc(auth_oauth_provider.data_endpoint, access_token)
        validation.update(data)
        return validation

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """ Retrieve and sign in the user corresponding to provider and validated access token """
        # Buscar el usuario por correo electrónico
        user = self.search([('login', '=', str(validation.get('email')))])
        
        # Comprobar si no se encontró el usuario
        if not user:
            # Verificar la configuración global de Odoo para la creación automática de usuarios
            if not self.env['ir.config_parameter'].sudo().get_param('auth_signup.allow_uninvited'):
                _logger.warning("Access Denied: Auto-signup is disabled and the user does not exist.")
                raise Exception("Access Denied: User creation is disabled.")
            
            # Si se permite la creación, crear el usuario
            user = self.create({
                'login': str(validation.get('email')),
                'name': str(validation.get('name'))
            })
            provider_id = self.env['auth.oauth.provider'].sudo().browse(provider)
            if provider_id.template_user_id:
                user.is_contractor = provider_id.template_user_id.is_contractor
                user.contractor = provider_id.template_user_id.contractor
                user.groups_id = [(6, 0, provider_id.template_user_id.groups_id.ids)]
        
        # Actualizar la información OAuth del usuario
        user.write({
            'oauth_provider_id': provider,
            'oauth_uid': validation['user_id'],
            'oauth_access_token': params['access_token'],
        })

        # Verificar si el usuario OAuth está correctamente vinculado
        oauth_uid = validation['user_id']
        try:
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                raise Exception("Access Denied")
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            return oauth_user.login
        except (Exception, Exception):
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except SignupError:
                raise Exception("Access Denied")
        return super(ResUsers, self)._auth_oauth_signin(provider, validation, params)

    @api.model
    def auth_oauth(self, provider, params):
        """ Take the access token to log in with the user account """
        if params.get('code'):
            validation = self._auth_oauth_code_validate(provider, params['code'])
            access_token = validation.pop('access_token')
            params['access_token'] = access_token
        else:
            access_token = params.get('access_token')
            validation = self._auth_oauth_validate(provider, access_token)
        if not validation.get('user_id'):
            if validation.get('id'):
                validation['user_id'] = validation['id']
            elif validation.get('oid'):
                validation['user_id'] = validation['oid']
            else:
                raise Exception("Access Denied")
        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            raise Exception("Access Denied")
        if provider and params:
            return self.env.cr.dbname, login, access_token
        return super(ResUsers, self).auth_oauth(provider, params)
