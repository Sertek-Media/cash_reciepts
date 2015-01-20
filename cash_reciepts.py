# -*- coding: utf-8 -*-
import datetime
import unicodedata
from openerp.osv import fields, osv
from openerp.tools.translate import _
from num2words import num2words
import openerp.addons.decimal_precision as dp
from openerp.addons.account_voucher import account_voucher
class account_cash_withdraw(osv.Model):
    _inherit = 'account.voucher'
    _desciption = "Print reciepts for cash Transactions"

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        return True

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        list = []
        cur_obj = self.pool.get('res.currency').read(cr,uid,currency_id,['name'],context)
        number = '%.2f' % amount
        list = str(number).split('.')
        cents_number = int(list[1])
        cents_name = (cents_number > 1) and 'Centų' or 'Cent'
        if list[1] == '00':
            res['value'].update({'num2words':num2words(abs(int(list[0])),lang='lt')+' '+str(cur_obj['name'])})
        else:
            res['value'].update({'num2words':num2words(abs(int(list[0])),lang='lt')+' '+str(cur_obj['name'])+' '+list[1]+' '+cents_name.decode('utf-8')})
        return res


#     def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
#         if context is None:
#             context = {}
#         ctx = context.copy()
#         ctx.update({'date': date})
#         #read the voucher rate with the right date in the context
#         currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
#         voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
#         ctx.update({
#             'voucher_special_currency': payment_rate_currency_id,
#             'voucher_special_currency_rate': rate * voucher_rate})
#         res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
#         vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
#         for key in vals.keys():
#             res[key].update(vals[key])
# #         l = int(amount)
# #         number_final=0
# # #         number_str = "%.2f" % amount
# #         numstring = str(amount)
# #         number = float(numstring[:numstring.find('.')+2])
# # #         number = float(number_str)
# #         print "==================================number",number
# #         temp = 1
# #         while (number*temp)%10 != 0:
# #             temp = temp *10
# #             print temp
# #             print number
# #         temp = temp /10
# #         number = number*temp
# #         try:    
# #             number_final = number%temp
# #         except:ZeroDivisionError
# #         print "---------number_final",round(number_final,2)
# #         number_final = int(number_final)
# #         decimal = num2words(abs(number_final),lang='lt')
# #         print "-------------------------------",decimal
#         cur_obj = self.pool.get('res.currency').read(cr,uid,currency_id,['name'],context)
# #         d = amount- int(amount)
# #         if d < 0.1:
# #             print "----------------------------------------d",d
# #             d = round(d,2)
# #             if d == 0:
# #                 words = num2words(abs(l),lang='lt')
# #                 res['value'].update({'num2words':words+'  '+str(cur_obj['name'])})
# #             elif d == 0.1:
# #                 words = num2words(abs(l),lang='lt')
# #                 res['value'].update({'num2words':words+'  '+str(cur_obj['name']+' '+'1'+' '+'Ct')})
# #             else :
# #                 k = int(d*100)
# #                 words_decimal = num2words(abs(k),lang='lt')
# #                 words = num2words(abs(l),lang='lt')
# #                 res['value'].update({'num2words':words+'  '+str(cur_obj['name']+' '+words_decimal+' '+'Ct')})
# #         else:
# #             words = num2words(abs(l),lang='lt')
# #             res['value'].update({'num2words':words+'  '+ str(cur_obj['name'])+'  '+decimal+' Ct'})
# #             print " ------------------------", words+'  '+decimal
# #         print res['value']['num2words']
#         return res

    def create(self,cr,uid,vals,context):
        journal_id = vals.get('journal_id',False)
        journal_vals = self.pool.get('account.journal').read(cr,uid,journal_id,['sequence_id','sequence_id2'],context)
        print journal_vals
        if context.get('source',False) == 'mod_wit':
            if journal_vals.get('sequence_id2',False):
                sequence_id2 = journal_vals.get('sequence_id2',False)[0]
                dict_code = self.pool.get('ir.sequence').read(cr,uid,sequence_id2,['code'],context)
                code = str(dict_code.get('code',False)) 
                custom_sequence = self.pool.get('ir.sequence').get(cr, uid, '%s' %code)
                vals['number'] = custom_sequence
        if context.get('source',False) == 'mod_rec':
            if journal_vals.get('sequence_id',False):
                sequence_id = journal_vals.get('sequence_id',False)[0]
                dict_code = self.pool.get('ir.sequence').read(cr,uid,sequence_id,['code'],context)
                code = str(dict_code.get('code',False)) 
                custom_sequence = self.pool.get('ir.sequence').get(cr, uid, '%s' %code)
                vals['number'] = custom_sequence
                custom_sequence = self.pool.get('ir.sequence').get(cr, uid, '%s' %code)
                vals['number'] = custom_sequence
        id = super(account_voucher.account_voucher,self).create(cr,uid,vals,context=context)
        return id
    
    def print_reciept_withdrawal(self,cr,uid,id,context):
        vals = self.read(cr,uid,id[0],[],context)
        if context is None:
            context = {}
        datas = {'ids': id}
        datas['model'] = 'account.voucher'
        datas['form'] = self.read(cr, uid, id,context)[0]
        if context.get('type',False) == 'withdrawal':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'cash_reciepts.report_cash_withdrawal_repeat',
                    'datas': datas,
                    'context':context
                }
        if context.get('type',False) == 'acceptance':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'cash_reciepts.report_cash_acceptance_repeat',
                    'datas': datas,
                    'context':context
                }

        return True
    
    def my_mehtod(self, cr, uid, context=None):
        return uid    
    
    _defaults ={
               'partner_responsible':my_mehtod
               } 
    _columns ={
               'partner_responsible':fields.many2one('res.users',"Partner"),
               'original_reciept':fields.binary('Original Reciept'),
               'final_reciept':fields.binary('Final Reciept'),
               'num2words':fields.char('Amount In words'),
               'sequence':fields.char('Sequence')
               }

class account_journal(osv.Model):
    
    _inherit = 'account.journal'
    _desciption = 'Withdrawal Sequence'
    
    _columns = {
                'sequence_id2':fields.many2one('ir.sequence','Cash Withdrawal Sequence'),
                }