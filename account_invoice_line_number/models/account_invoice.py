##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice'

    id_pa = fields.Many2one('purchase.order', string='Título de PA', size=20)
    code_pa = fields.Char('Código de PA', compute='_get_code_pa')

    @api.one
    @api.depends('id_pa')
    def _get_code_pa(self): 
        for rec in self.id_pa:
            self.code_pa = rec.code_pa

class AccountInvoiceLine(models.Model):
    _inherit = 'res.partner.bank'

    code_cci = fields.Char('CCI', size=20)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    number = fields.Integer(compute='_compute_number', store=True)

    @api.depends('sequence', 'invoice_id')
    def _compute_number(self):
        for invoice in self.mapped('invoice_id'):
            number = 1
            for line in invoice.invoice_line_ids:
                line.number = number
                number += 1

class AccountInvoiceLine(models.Model):
    _inherit = 'account.payment'

    register_id = fields.Char('Registro ID', size=20)


