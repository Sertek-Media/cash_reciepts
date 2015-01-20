from openerp.report import report_sxw

class report_cash_rml_withdrawal(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_cash_rml_withdrawal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
#             'get_subject_total': self.get_subject_total,
        })

#     def get_subject_total(self, exam):
#         total = 0
#         for line in exam.exam_line:
#             total += line.total_mark
#         return total

#report_result is a service name of a report.

report_sxw.report_sxw('report.report_cash_withdrawal_rml', 'account.voucher',
       'addons/cash_reciepts/report/report_cash_withdrawal_rml.rml',parser=report_cash_rml_withdrawal, header=False)
