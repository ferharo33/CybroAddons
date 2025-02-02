# -*- coding: utf-8 -*-
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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class LoanRequest(models.Model):
    """Can create new loan requests and manage records"""
    _name = 'loan.request'
    _inherit = ['mail.thread']
    _description = 'Loan Request'

    name = fields.Char(string='Loan Reference', readonly=True,
                       copy=False, help="Sequence number for loan requests",
                       default=lambda self: 'New')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.
                                  currency_id)
    loan_type_id = fields.Many2one('loan.type', string='Loan Type',
                                   required=True, help="Can choose different "
                                                       "loan types suitable")
    loan_amount = fields.Float(string="Loan Amount",
                               help="Total loan amount", )
    disbursal_amount = fields.Float(string="Disbursal Amount",
                                    help="Total loan amount "
                                         "available to disburse")
    tenure = fields.Integer(string="Periods", default=1,
                            help="Installment period")
    # Campo que almacena el valor real del interés en el modelo loan.request
    interest_rate = fields.Float(
        string='Interest Rate (Real)', 
        digits=(16, 10),  # Asegúrate de permitir decimales para cálculos precisos
        help="Valor real del interés (por ejemplo, 0.0469 para 4.69%)")

    # Campo para visualización en porcentaje
    interest_rate_percentage = fields.Float(
        string='Interest Rate (%)',
        compute='_compute_interest_rate_percentage',
        inverse='_inverse_interest_rate_percentage',
        digits=(16, 4),
        store=True,
        help="Visualización del interés en porcentaje. Ejemplo: 4.69")

    date = fields.Date(string="Date", default=fields.Date.today(),
                       readonly=True, help="Date")
    partner_id = fields.Many2one('res.partner', string="Partner",
                                 required=True,
                                 help="Partner")
    repayment_lines_ids = fields.One2many('repayment.line',
                                          'loan_id',
                                          string="Loan Line", index=True,
                                          help="Repayment lines")
    documents_ids = fields.Many2many('loan.documents',
                                     string="Proofs",
                                     help="Documents as proof")
    img_attachment_ids = fields.Many2many('ir.attachment',
                                          relation="m2m_ir_identity_card_rel",
                                          column1="documents_ids",
                                          string="Images",
                                          help="Image proofs")
    journal_id = fields.Many2one('account.journal',
                                 string="Journal",
                                 help="Journal types",
                                 domain="[('type', '=', 'purchase'),"
                                        "('company_id', '=', company_id)]",
                                 )
    debit_account_id = fields.Many2one('account.account',
                                       string="Debit account",
                                       help="Choose account for "
                                            "disbursement debit")
    credit_account_id = fields.Many2one('account.account',
                                        string="Credit account",
                                        help="Choose account for "
                                             "disbursement credit")
    reject_reason = fields.Text(string="Reason", help="Displays "
                                                      "rejected reason")
    request = fields.Boolean(string="Request",
                             help="For monitoring the record")
    state = fields.Selection(string='State',
        selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'),
                   ('waiting', 'Waiting For Approval'),
                   ('approved', 'Approved'), ('disbursed', 'Disbursed'),
                   ('rejected', 'Rejected'), ('closed', 'Closed')],
        copy=False, tracking=True, default='draft', help="Loan request states")

    @api.depends('interest_rate')
    def _compute_interest_rate_percentage(self):
        """Compute para mostrar el valor del interés como porcentaje en la vista."""
        for record in self:
            record.interest_rate_percentage = record.interest_rate * 100

    def _inverse_interest_rate_percentage(self):
        """Permite al usuario ingresar el valor como porcentaje y lo almacena como real."""
        for record in self:
            record.interest_rate = record.interest_rate_percentage / 100

    @api.model
    def create(self, vals):
        """create  auto sequence for the loan request records"""
        loan_count = self.env['loan.request'].search(
            [('partner_id', '=', vals['partner_id']),
             ('state', 'not in', ('draft', 'rejected', 'closed'))])
        if loan_count:
            for rec in loan_count:
                if rec.state != 'closed':
                    raise UserError(
                        _('The partner has already an ongoing loan.'))
        else:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'increment_loan_ref')
            res = super().create(vals)
            return res

    @api.onchange('loan_type_id')
    def _onchange_loan_type_id(self):
        """Changing field values based on the chosen loan type"""
        type_id = self.loan_type_id
        self.loan_amount = type_id.loan_amount
        self.disbursal_amount = type_id.disbursal_amount
        self.tenure = type_id.tenure
        self.interest_rate = type_id.interest_rate
        self.documents_ids = type_id.documents_ids

    def action_loan_request(self):
        """Changes the state to confirmed and send confirmation mail"""
        self.write({'state': "confirmed"})
        partner = self.partner_id
        loan_no = self.name
        subject = 'Loan Confirmation'
        message = (f"Dear {partner.name},<br/> This is a confirmation mail "
                   f"for your loan{loan_no}. We have submitted your loan "
                   f"for approval.")
        outgoing_mail = self.company_id.email
        mail_values = {
            'subject': subject,
            'email_from': outgoing_mail,
            'author_id': self.env.user.partner_id.id,
            'email_to': partner.email,
            'body_html': message,
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()

    def action_request_for_loan(self):
        """Change the state to waiting for approval"""
        if self.request:
            self.write({'state': "waiting"})
        else:
            message_id = self.env['message.popup'].create(
                {'message': _("Compute the repayments before requesting")})
            return {
                'name': _('Repayment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.popup',
                'res_id': message_id.id,
                'target': 'new'
            }

    def action_loan_approved(self):
        """Change to Approved state"""
        self.write({'state': "approved"})

    def action_disburse_loan(self):
        """Disbursing the loan to customer and creating journal
         entry for the disbursement"""
        self.write({'state': "disbursed"})
        for loan in self:
            amount = loan.disbursal_amount
            loan_name = loan.partner_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.debit_account_id.id
            credit_account_id = loan.credit_account_id.id
            date_now = loan.date
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': date_now,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': date_now,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'name': f'DIS / {reference}',
                'narration': reference,
                'ref': reference,
                'journal_id': journal_id,
                'date': date_now,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.action_post()
        return True

    def action_close_loan(self):
        """Closing the loan"""
        demo = []
        for check in self.repayment_lines_ids:
            if check.state == 'unpaid':
                demo.append(check)
        if len(demo) >= 1:
            message_id = self.env['message.popup'].create(
                {'message': _("Pending Repayments")})
            return {
                'name': _('Repayment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.popup',
                'res_id': message_id.id,
                'target': 'new'
            }
        self.write({'state': "closed"})

    def action_loan_rejected(self):
        """You can add reject reasons here"""
        return {'type': 'ir.actions.act_window',
                'name': 'Loan Rejection',
                'res_model': 'reject.reason',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_loan': self.name}
                }

    def action_compute_repayment(self):
        """This automatically creates the installment the employee needs to pay to
        company based on payment start date and the number of installments."""
        self.request = True
        for loan in self:
            loan.repayment_lines_ids.unlink()
            
            # Determinar el intervalo de pagos en base al tipo de plan de amortización
            if loan.loan_type_id.tenure_plan == 'monthly':
                date_start = datetime.strptime(str(loan.date), '%Y-%m-%d') + relativedelta(months=1)
                interval = relativedelta(months=1)
            elif loan.loan_type_id.tenure_plan == 'biweekly':  # Nuevo plan quincenal
                date_start = datetime.strptime(str(loan.date), '%Y-%m-%d') + relativedelta(days=15)
                interval = relativedelta(days=15)
            else:
                raise UserError(_("El plan de amortización seleccionado no es válido."))

            amount = loan.loan_amount / loan.tenure
            interest = loan.loan_amount * loan.interest_rate
            interest_amount = interest / loan.tenure
            total_amount = amount + interest_amount
            partner = self.partner_id

            for rand_num in range(1, loan.tenure + 1):
                self.env['repayment.line'].create({
                    'name': f"{loan.name}/{rand_num}",
                    'partner_id': partner.id,
                    'date': date_start,
                    'amount': amount,
                    'interest_amount': interest_amount,
                    'total_amount': total_amount,
                    'interest_account_id': self.env.ref('advanced_loan_management.'
                                                        'loan_management_'
                                                        'inrst_accounts').id,
                    'repayment_account_id': self.env.ref('advanced_loan_management.'
                                                         'demo_'
                                                         'loan_accounts').id,
                    'loan_id': loan.id})
                
                # Actualizar la fecha para el siguiente periodo de amortización
                date_start += interval
        return True

