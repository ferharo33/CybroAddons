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
import json
import requests
from odoo import fields, models, _
from odoo.exceptions import UserError


class TicketHelpdesk(models.Model):
    """In this class there are functions for create a ticket in to zendesk,
    update a ticket, and delete a ticket from zendesk"""
    _inherit = 'ticket.helpdesk'

    zendesk_ticket_no = fields.Char(string='Zendesk Ticket Id',
                                    help='Shows the Id of ticket in Zendesk',
                                    readonly=True)
    is_ticket_from_zendesk = fields.Boolean(string='Ticket From Zendesk',
                                            help='Is this a ticket from'
                                                 ' Zendesk')
    email = fields.Char(string='Email', help='Shows the email of the customer',
                        required=True)

    def action_create_to_zendesk(self):
        """This function will help to create a ticket in Zendesk"""
        company_domain = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_domain')
        company_email = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_email')
        password = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.password')
        api_token = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.api_key')
        if self.zendesk_ticket_no:
            zen_id_search_url = f'https://{company_domain}.zendesk.com/api/v2/tickets/{self.zendesk_ticket_no}.json'
            zen_id_search_response = requests.get(zen_id_search_url,
                                                  timeout=180, auth=(
                company_email, password))
            if zen_id_search_response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Warning"),
                        'message': _("Ticket already exists"),
                        'sticky': False,
                    },
                }

        priority = {
            '2': 'normal',
            '3': 'high',
            '4': 'urgent'
        }
        zen_prio = priority.get(self.priority, 'None')
        headers = {'content-type': 'application/json'}
        customer_search_url = f'https://{company_domain}.zendesk.com/api/v2/users/search.json?query=email:{self.email}'
        search_response = requests.get(customer_search_url,
                                       auth=(company_email, password),
                                       timeout=20)
        if search_response.status_code == 200:
            results = search_response.json().get('users')
            if not results:
                # Customer does not exist, create a new user
                data = {
                    'user': {
                        'name': self.customer_id.name,
                        'email': self.email,
                    }
                }
                user_url = f'https://{company_domain}.zendesk.com/api/v2/users.json'
                user_response = requests.post(user_url, json=data,
                                              auth=(company_email, password),
                                              headers=headers)
                if user_response.status_code != 201:
                    raise UserError(_(user_response.json()['error']))

        data = {'ticket': {'subject': self.subject, 'priority': zen_prio,
                           'comment': {'body': self.description},
                           'requester': {
                               'name': self.customer_id.name,
                               'email': self.customer_id.email
                           }
                           }}
        url = f'https://{company_domain}.zendesk.com/api/v2/tickets.json'
        response = requests.post(url, data=json.dumps(data),
                                 auth=(f"{company_email}/token", api_token),
                                 headers=headers)
        if response.status_code == 201:
            self.zendesk_ticket_no = response.json()['ticket']['id']
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success!"),
                    'message': _("Successfully Created the ticket in Zendesk"),
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Error!"),
                'message': _(
                    "Creation of Zendesk ticket seems to have failed!"),
                'sticky': False,
            }
        }

    def action_update_zendesk_ticket(self):
        """This function is used to update a ticket from oddo"""
        company_domain = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_domain')
        company_email = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_email')
        api_token=self.env['ir.config_parameter'].sudo().get_param('odoo_zendesk_connector.api_key')
        zen_id = self.zendesk_ticket_no
        priority = {
            '1': 'low',
            '2': 'normal',
            '3': 'high',
            '4': 'urgent'
        }
        zen_prio = 'None'
        if self.priority in priority:
            zen_prio = priority[self.priority]
        data = {
            'ticket': {
                'comment': {'body': self.description},
                'priority': zen_prio,
                'subject': self.subject,
                'requester': {
                    'name': self.customer_name,  # Add the customer name field
                    'email': self.email  # Add the customer email field
                }
            }
        }
        url = f'https://{company_domain}.zendesk.com/api/v2/tickets/{zen_id}.json'
        headers = {'content-type': 'application/json'}
        response = requests.put(url, data=json.dumps(data),
                                auth = (f"{company_email}/token", api_token),
                                headers=headers)
        if response.status_code != 200:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error!"),
                    'message': _("Updation of the ticket seems to be failed"),
                    'sticky': False,
                }
            }
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Success!"),
                'message': _("Successfully Updated the ticket"),
                'sticky': False,
            }
        }

    def action_delete_zendesk_ticket(self):
        """This function is used to delete a ticket from zendesk"""
        company_domain = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_domain')
        company_email = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.company_email')
        api_token = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_zendesk_connector.api_key')
        zendesk_id = self.zendesk_ticket_no
        headers = {'Content-Type': 'application/json'}
        url = f'https://{company_domain}.zendesk.com/api/v2/tickets/{zendesk_id}.json'
        response = requests.delete(url, auth=(f"{company_email}/token", api_token),
                                   headers=headers, timeout=180)
        if response.status_code == 204:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Success!"),
                    'message': _("Successfully deleted the tickets"),
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Error"),
                    'message': _("Have issues with deleting the ticket"),
                    'sticky': False,
                }
            }
