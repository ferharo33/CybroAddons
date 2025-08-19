# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Ajith V (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
from odoo import models


class PosSession(models.Model):
    """inherited the pos session and loaded models to pos"""
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        """load the models to pos"""
        res = super()._pos_ui_models_to_load()
        res.append('pos.keyboard.shortcut')
        res.append('pos.payment.method.key')
        return res

    def _loader_params_pos_keyboard_shortcut(self):
        """To load pos keyboard shortcut fields in pos"""
        return {
            'search_params': {
                'fields': [],
                'domain': [('id', '=', self.config_id.select_shortcut_id.id)]
            },
        }

    def _get_pos_ui_pos_keyboard_shortcut(self, params):
        """set the get function for return the fields values"""
        return self.env['pos.keyboard.shortcut'].search_read(
            **params['search_params'])

    def _loader_params_pos_payment_method_key(self):
        """To load pos payment method key fields in pos"""
        return {
            'search_params': {
                'fields': [],
                'domain': [('keyboard_shortcut_id', '=',
                            self.config_id.select_shortcut_id.id)]
            },
        }

    def _get_pos_ui_pos_payment_method_key(self, params):
        """set the get function for return the fields values"""
        return self.env['pos.payment.method.key'].search_read(
            **params['search_params'])
