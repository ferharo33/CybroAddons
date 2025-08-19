# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Gayathri V (Contact : odoo@cybrosys.com)
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
#############################################################################
from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        res.append('pos.order.question')
        return res

    def _get_pos_ui_pos_order_question(self, params):
        """Adding search params into pos_order_questions"""
        return self.env['pos.order.question'].search_read(
            **params['search_params'])

    def _loader_params_pos_order_question(self):
        """Loading fields of model pos_order_question"""
        return {'search_params': {'domain': [], 'fields': ['name']}}

    def _loader_params_product_product(self):
        """Loading newly added field from product_product into pos_session"""
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('order_question_ids')
        return result
