# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Subina P (odoo@cybrosys.com)
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
################################################################################
from odoo import models


class Cashflow(models.Model):
    """ Class for getting report data """
    _name = "cashflow"
    _description = 'Report advanced cash flows'

    def get_report_values(self, data=None):
        """
          Fetches and returns the report values for the cashflow report.
          :param data: Dictionary containing parameters for fetching the report data.
          :return: Dictionary containing fetched data, journal results, and account results.
              """
        account_res = []
        journal_res = []
        # Query to fetch all data without date filtration
        query = """
                SELECT DISTINCT aa.name, aa.code, 
                SUM(aml.debit) AS total_debit, 
                SUM(aml.credit) AS total_credit 
            FROM (
                SELECT am.* 
                FROM account_move AS am
                LEFT JOIN account_move_line aml ON aml.move_id = am.id
                LEFT JOIN account_account aa ON aa.id = aml.account_id
                WHERE am.state = 'posted'
            ) am
            LEFT JOIN account_move_line aml ON aml.move_id = am.id
            LEFT JOIN account_account aa ON aa.id = aml.account_id
            GROUP BY aa.name, aa.code
        """
        cr = self._cr
        cr.execute(query)
        fetched_data = cr.dictfetchall()
        for account in self.env['account.account'].search([]):
            child_lines = self._get_lines(account, data)
            if child_lines:
                account_res.append(child_lines)
        return {
            'fetched_data': fetched_data,
            'journal_res': journal_res,
            'account_res': account_res,
        }

    def _get_lines(self, account, data):
        """ fetch values for lines"""
        user_lang = self.env.user.lang
        # Query to fetch values without date filtration
        query = """SELECT aml.id, aml.move_id, aml.account_id, aj.name ->'%s' as name, am.name as move_name, 
                          SUM(aml.debit) AS total_debit, 
                          SUM(aml.credit) AS total_credit 
                   FROM (
                       SELECT am.* 
                       FROM account_move as am
                       LEFT JOIN account_move_line aml ON aml.move_id = am.id
                       LEFT JOIN account_account aa ON aa.id = aml.account_id
                       WHERE am.state = 'posted'
                   ) am
                   LEFT JOIN account_move_line aml ON aml.move_id = am.id
                   LEFT JOIN account_account aa ON aa.id = aml.account_id
                   LEFT JOIN account_journal aj ON aj.id = am.journal_id
                   WHERE aa.id = %d 
                   GROUP BY aml.id, am.name, aml.account_id, aj.name""" % (user_lang, account.id)

        cr = self._cr
        cr.execute(query)
        fetched_data = cr.dictfetchall()
        # Another query to fetch journal lines without date filtration
        sql = """SELECT aa.name ->'%s' as account_name, aj.id, aj.name ->'%s' as name, 
                          SUM(aml.debit) AS total_debit, 
                          SUM(aml.credit) AS total_credit 
                   FROM (
                       SELECT am.* 
                       FROM account_move as am
                       LEFT JOIN account_move_line aml ON aml.move_id = am.id
                       LEFT JOIN account_account aa ON aa.id = aml.account_id
                       WHERE am.state = 'posted'
                   ) am
                   LEFT JOIN account_move_line aml ON aml.move_id = am.id
                   LEFT JOIN account_account aa ON aa.id = aml.account_id
                   LEFT JOIN account_journal aj ON aj.id = am.journal_id
                   WHERE aa.id = %d
                   GROUP BY aa.name, aj.name, aj.id""" % (account.name, user_lang, account.id)
        cr.execute(sql)
        fetch_data = cr.dictfetchall()
        if fetched_data:
            return {
                'account': account.name,
                'code': account.code,
                'move_lines': fetched_data,
                'journal_lines': fetch_data,
            }
