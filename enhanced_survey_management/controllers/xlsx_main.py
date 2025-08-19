# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Nihala KP (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0(OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
import io
import json
from datetime import datetime

from odoo import http
from odoo.http import content_disposition, request
from odoo.tools.misc import xlsxwriter


class XlsxReportController(http.Controller):
    """Inherited http.Controller to add custom route"""

    @http.route('/xlsx_report/<model("survey.survey"):survey_id>',
                type='http', auth='user', csrf=False)
    def get_report_xlsx(self, survey_id=None, **args):
        """ Function to create and print XLSX report"""
        user_input_ids = request.env['survey.user_input'].search(
            [("survey_id", '=', survey_id.id)])
        answers, title = [], ''
        for rec in user_input_ids:
            for res in rec:
                answer=''
                name = ''
                for new in res.user_input_line_ids:
                    print(new.question_id)
                    if new.question_id.question_type in ['barcode', 'qr']:
                        continue
                    new_dt = str(rec.create_date).split('.')
                    if new.question_id.question_type == 'address':
                        data=json.loads(new.display_name)
                        for key in data:
                            if data[key]:
                                answer+=f'{data[key]},'
                        answers.append([rec.id, rec.nickname, new_dt[0],
                                        new.question_id.title, answer])
                    elif new.question_id.question_type == 'name':
                        data = json.loads(new.display_name)
                        for key in data:
                            if data[key]:
                                name += f'{data[key]} '
                        answers.append([rec.id, rec.nickname, new_dt[0],
                                        new.question_id.title, name])
                    elif new.question_id.question_type == 'time':
                        # Convert time to 12-hour format
                        time_str = new.display_name
                        time_parts = time_str.split('.')
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1]) if len(
                                time_parts) > 1 else 0

                            # Handle 24-hour to 12-hour conversion
                        time_obj = datetime.strptime(f'{hours}:{minutes}',
                                                         '%H:%M')
                        time_12hr = time_obj.strftime('%I:%M %p')
                        answers.append([rec.id, rec.nickname, new_dt[0],
                                        new.question_id.title, time_12hr])


                    else:
                        answers.append([rec.id, rec.nickname, new_dt[0],
                                    new.question_id.title, new.display_name])
        answers.reverse()
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition',
                 content_disposition(survey_id.title + '.xlsx'))
            ]
        )
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        sheet.set_column(1, 0, 25)
        sheet.set_column(2, 0, 25)
        sheet.set_column(3, 3, 50)
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        sub_title = workbook.add_format(
            {'align': 'right', 'bold': True, 'font_size': '12px'})
        sub_title_content = workbook.add_format(
            {'align': 'left', 'bold': True, 'font_size': '12px'})
        txt = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A2:D3', 'SURVEY MANAGEMENT REPORT', head)
        sheet.write('A4', 'Title :', sub_title)
        sheet.merge_range('B4:C4', survey_id.title, sub_title_content)
        sheet.merge_range('A6:A7', 'Partner', cell_format)
        sheet.merge_range('B6:B7', 'Submission Date & Time', cell_format)
        sheet.merge_range('C6:C7', 'Question', cell_format)
        sheet.merge_range('D6:D7', 'Answer', cell_format)
        row = 7
        column = 0
        for rec in answers:
            sheet.write(row, column, rec[1], txt)
            sheet.write(row, column + 1, rec[2], txt)
            sheet.write(row, column + 2, rec[3], txt)
            sheet.write(row, column + 3, rec[4], txt)
            row = row + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response
