################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Megha (odoo@cybrosys.com)
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
from odoo import api, fields, models


class LoanTypes(models.Model):
    """Create different types of Loans, And can wisely choose while requesting
     for loan"""
    _name = 'loan.type'
    _inherit = ['mail.thread']
    _description = 'Loan Type'

    name = fields.Char(string='Name', help="LoanType Name")
    loan_amount = fields.Integer(string='Loan Amount', help="Loan Amount")
    tenure = fields.Integer(string='Periods', default='1',
                            help="Amortization period")
     # Añadir opción de plan quincenal en lugar de solo mensual
    tenure_plan = fields.Selection(
        [('monthly', 'Mensual'), ('biweekly', 'Quincenal')],
        string="Plan de Amortización", default='monthly',
        help="Selecciona el plan de amortización: Mensual o Quincenal")
    
    # Campo que almacena el valor real del interés
    interest_rate = fields.Float(
        string='Interest Rate (Real)', 
        digits=(16, 10),  # Asegúrate de permitir muchos decimales para cálculos precisos
        help="Valor real del interés (por ejemplo, 0.0469 para 4.69%)")

    # Campo para visualización en porcentaje
    interest_rate_percentage = fields.Float(
        string='Interest Rate (%)',
        compute='_compute_interest_rate_percentage',
        inverse='_inverse_interest_rate_percentage',
        digits=(16, 4),
        store=True,
        help="Visualización del interés en porcentaje. Ejemplo: 4.69")


    disbursal_amount = fields.Float(string='Disbursal Amount',
                                    compute='_compute_disbursal_amount',
                                    help="Total Amount To Be Disbursed")
    documents_ids = fields.Many2many('loan.documents',
                                     string="Documents",
                                     help="Personal Proofs")
    processing_fee = fields.Integer(string="Processing Fee",
                                    help="Amount For Initializing The Loan")
    note = fields.Text(string="Criteria", help="Criteria for approving "
                                               "loan requests")
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True, help="Company Name",
                                 default=lambda self: self.env.company, )

    @api.depends('processing_fee')
    def _compute_disbursal_amount(self):
        """Calculating amount for disbursing"""
        self.disbursal_amount = self.loan_amount - self.processing_fee

    @api.depends('interest_rate')
    def _compute_interest_rate_percentage(self):
        """Compute para mostrar el valor del interés como porcentaje en la vista."""
        for record in self:
            record.interest_rate_percentage = record.interest_rate * 100

    def _inverse_interest_rate_percentage(self):
        """Permite al usuario ingresar el valor como porcentaje y lo almacena como real."""
        for record in self:
            record.interest_rate = record.interest_rate_percentage / 100
