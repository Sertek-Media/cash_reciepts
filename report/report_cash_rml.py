from openerp.report import report_sxw
class report_cash_rml(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_cash_rml, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
        })

#     def get_subject_total(self, exam):
#         total = 0
#         for line in exam.exam_line:
#             total += line.total_mark
#         return total

#report_result is a service name of a report.

report_sxw.report_sxw('report.report_cash_acceptance_rml', 'account.voucher',
        'addons/cash_reciepts/report/report_cash_acceptance_rml.rml',parser=report_cash_rml, header=False)
