# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, models
from datetime import datetime

class ProductProduct(models.Model):
    """This class extends the 'product.product' model to enhance its functionality."""
    _inherit = 'product.product'

    @api.depends('product_tmpl_id.write_date')
    def _compute_write_date(self):
        """Compute the write date for the product record.
           This method computes the write date for each product record by taking the maximum of the current
           write date of the product and the write date of the related product template. If the product's write
           date is not set, the current date and time are used. If the product template's write date is not set,
           a minimum datetime value (datetime.min) is used.
           This ensures that the write date reflects the most recent modification date between the product and
           its template."""
        for record in self:
            record_write_date = record.write_date or self.env.cr.now()
            tmpl_write_date = record.product_tmpl_id.write_date or datetime.min
            record.write_date = max(record_write_date, tmpl_write_date)
