# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _ , SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date


class SprogroupPurchaseRequest(models.Model):

    _inherit = 'sprogroup.purchase.request'

    type_sdp = fields.Selection(related='id_purchase_order.type_sdp', string='Tipo de SdP')
    sdp_sequence = fields.Char(related='id_purchase_order.sdp_sequence', string='SdP Secuencia')

    @api.depends('adq_type')
    @api.model
    def create(self,vals):
        #for rec in self:
        if vals['adq_type'] == 'Bienes':
            vals['code'] = self.env['ir.sequence'].next_by_code('adq.sequence')
        elif vals['adq_type'] == 'Servicio':
            vals['code'] = self.env['ir.sequence'].next_by_code('adqs.sequence')
        elif vals['adq_type'] == 'Contrato':
            vals['code'] = self.env['ir.sequence'].next_by_code('adqc.sequence')
        return super(SprogroupPurchaseRequest, self).create(vals) 

class SprogroupPurchaseRequestLine(models.Model):
    _inherit ='sprogroup.purchase.request.line'
    
    type_sdp = fields.Selection(related='request_id.type_sdp',
                             string='Tipo SdP', track_visibility='onchange', readonly=True,
                             store=True)
    sdp_sequence = fields.Char(related='request_id.sdp_sequence',
                             string='SdP Secuencia', track_visibility='onchange', readonly=True,
                             store=True)

class StatusPartner(models.Model):
    _name = 'status.partner'
 
    name = fields.Char('Estado de Proveedor', size=20)
    #date_evaluation = fields.Date('Ultima Fecha Evaluacion', track_visibility='onchange')

class PaymentType(models.Model):
    _name = 'payment.type'
 
    name = fields.Char('Forma de pago', size=20)

class Criticality(models.Model):
    _name = 'criticality.partner'
 
    name = fields.Char('Criticidad', size=20)


class ResPartner(models.Model):
    _inherit = "res.partner"

    #payment_type = fields.Selection(selection_add=[('Transferencia', 'Transferencia'), ('Cheque', 'Cheque'), ('Letra', 'Letra'), ('Efectivo', 'Efectivo')])
    #criticality_sel = fields.Selection(#comodel_name='criticality.partner', string='Criticidad', size=20, delegate=True), 
    #    selection_add='_get_selection')
    #status_partners = fields.Selection([('Esporádico', 'Esporádico'), ('Frecuente', 'Frecuente'), ('Convenio', 'Convenio')])
    main_products = fields.Many2many('product.category', string='Principales Productos', size=20)
    criticality = fields.Many2many('criticality.partner', string='Criticidad', size=20)
    payment_type = fields.Many2many('payment.type', string='Forma de pago', size=20)
    #date_evaluation = fields.Date('Ultima Fecha Evaluacion', related='payment_type.date_evaluation', track_visibility='onchange')
    status_partner = fields.Many2many('status.partner', string='Estado proveedor', size=20)
    description_partner = fields.Html(string='Description')
    catalog = fields.Char('Catalogo', size=200, store=True)
    date_evaluation = fields.Date('Fecha Evaluacion Final', size=20, store=True)
    eva = fields.Integer('Resultado Evaluacion', size=3, store=True)
    #criticality = fields.Many2one(comodel_name='criticality.partner', string='Criticidad', size=20, delegate=True)#, selection='_get_selection')
    
    #def _get_selection(self, cr, uid, context=None):
    #   return ([('Critico','Normal')])

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    """@api.constrains('order_line')
    def _check_order_lines_sequence(self):
        all_sequences = self.order_line.mapped('sequence')
        sequences = list(set(all_sequences))
        if len(all_sequences) != len(sequences):
            raise ValidationError(
                _('La secuencia debe ser unica por Orden de Compra!') + ".\n" +
                _('Las siguientes secuencias ya se encuentran en uso') + ":\n" +
                str(sequences))"""

    type_order = fields.Selection([('OC', 'OC'),('OS', 'OS'),('CTIT','CTIT')])
    order_sequence = fields.Char(string='Secuencia de Orden', readonly=True, store=True, size=30)
    type_sdp = fields.Selection([('SB', 'SB'),('SS', 'SS'),('SC','SC')])
    sdp_sequence = fields.Char(string='Secuencia de SdP', readonly=True, store=True)
    state_draft = fields.Boolean(string='Draft Start', compute='_get_state_draft')
    state_sdp_sequence = fields.Boolean(string='Sdp Boolean', compute='_get_sdp_sequence')
    state_order_sequence = fields.Boolean(string='Order Boolean', compute='_get_order_sequence')
    status_supplier = fields.Selection([('Cotizado', 'Cotizado'), ('Seleccionado', 'Seleccionado'), ('Referencial', 'Referencial')])
    date_due = fields.Date(string='Due Date', compute='_compute_date_due')
    payment_days = fields.Integer(string='Plazo de Pago', compute='_compute_payment_days')
    location_supplier = fields.Char('Lugar de Entrega Proveedor', size=30, track_visibility='onchange')
    buyer = fields.Selection([('Tactical IT', 'Tactical IT'),('Consorcio', 'Consorcio')])
    state = fields.Selection(selection_add=[('Entregado', 'Entregado')])
    #purchase_order_line_id = fields.One2many('purchase.order.line','order_id', string='Purchase Order Line', copy=True, readonly=True)

    
    @api.multi
    def button_delivered(self):
        return self.write({'state': 'Entregado'})

    @api.one
    @api.onchange('payment_term_id.line_ids')
    def _compute_payment_days(self):
        #payment_id = self.payment_term_id.id
        if self.payment_term_id:    
            pterm_list = self.payment_term_id.line_ids #.search([('payment_id', '=', self.payment_term_id.id)])
            self.payment_days = max(line.days for line in pterm_list)

    @api.one
    @api.onchange('payment_term_id.line_ids' 'date_planned')
    def _compute_date_due(self):
        payment_id = self.payment_term_id.id
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        date_planned = datetime.strptime(self.date_planned, DATETIME_FORMAT)
        if self.payment_term_id:    
            pterm_list = self.payment_term_id.line_ids #.search([('payment_id', '=', self.payment_term_id.id)])
            #pterm_list = pterm.with_context(currency_id=self.company_id.currency_id.ids).compute(value=1, date_ref=date_planned)[0]
            time_due = max(line.days for line in pterm_list)
            due_days = timedelta(days=time_due)
            self.date_due = date_planned + due_days

    @api.multi
    def write(self,vals):
        if vals.get('type_order') == 'OC':
            vals['order_sequence'] = self.env['ir.sequence'].next_by_code('oc.sequence')
        elif vals.get('type_order') == 'OS':
            vals['order_sequence'] = self.env['ir.sequence'].next_by_code('os.sequence')
        elif vals.get('type_order') == 'CTIT':
            vals['order_sequence'] = self.env['ir.sequence'].next_by_code('ctit.sequence') + '/' + self.code_project
        return super(PurchaseOrder, self).write(vals)
    

    @api.depends('type_sdp', 'type_order')
    @api.model
    def create(self,vals):
        if vals['type_sdp'] == 'SB':
            vals['sdp_sequence'] = self.env['ir.sequence'].next_by_code('sdb.sequence')
        elif vals['type_sdp'] == 'SS':
            vals['sdp_sequence'] = self.env['ir.sequence'].next_by_code('sds.sequence')
        elif vals['type_sdp'] == 'SC':
            vals['sdp_sequence'] = self.env['ir.sequence'].next_by_code('sdc.sequence')
        return super(PurchaseOrder, self).create(vals)        

    @api.multi
    def name_get(self):
        res = []
        for element in self:
            if element.state == 'draft':
                #name = str(element.type_sdp)
                #name += '-'
                name = str(element.sdp_sequence)
                res.append((element.id, name))
            elif element.state == 'cancel':
                #name = str(element.type_sdp)
                #name += '-'
                name = str(element.order_sequence)
                res.append((element.id, name))
            else:
                #name = str(element.type_sdp)
                #name += '-'
                name = str(element.order_sequence)
                """
                name += ' ('
                name += str(element.type_order)
                name += '-'
                name += str(element.order_sequence)
                name += ')'
                """
                res.append((element.id, name))
        return res

    @api.one
    @api.depends('state')
    def _get_state_draft(self):
        if(self.state == 'draft'):
            self.state_draft = True
        else:
            self.state_draft = False

    @api.one
    @api.depends('sdp_sequence')
    def _get_sdp_sequence(self):
        if self.sdp_sequence:
            self.state_sdp_sequence = True
        else:
            self.state_sdp_sequence = False

    @api.one
    @api.depends('order_sequence')
    def _get_order_sequence(self):
        if self.order_sequence:
            self.state_order_sequence = True
        else:
            self.state_order_sequence = False

    """
    id_pa = fields.Many2one(comodel_name='sprogroup.purchase.request', delegate=True, string='Título de PA', size=20)
    code_project = fields.Char('Código de Proyecto', compute='_get_code_project')
    component_project = fields.Char('Componente de Proyecto', compute='_get_component_project')
    code_pa = fields.Char('Código de PA', compute='_get_code_pa')

    @api.one
    @api.depends('id_pa')
    def _get_code_project(self): 
        for rec in self.id_pa:
            self.code_project = rec.code_project

    #@api.one
    #@api.depends('id_pa')
    #def _get_component_project(self): 
    #    for rec in self.id_pa:
    #        self.component_project = rec.component_project

    @api.one
    @api.depends('id_pa')
    def _get_code_pa(self): 
        for rec in self.id_pa:
            self.code_pa = rec.code 
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    """
    

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def default_get(self, fields_list):
        """Overwrite the default value of the sequence field taking into account
        the current number of lines in the purchase order. If is not call from
        the purchase order will use the default value.
        """
        res = super(PurchaseOrderLine, self).default_get(fields_list)
        res.update({'sequence': len(self._context.get('order_line', [])) + 1})
        return res

    code_product_id = fields.Char(string='Codigo Interno Producto' , related='product_id.code_final')
    state = fields.Selection(string='State', related='order_id.state')
    active_product = fields.Boolean(related='product_id.active', string='Activo Producto')
    date_start_up = fields.Date('Fecha Puesta en Obra', track_visibility='onchange')
    date_order = fields.Datetime('Fecha de emision de OC', track_visibility='onchange', related='order_id.date_order')
    type_sdp = fields.Selection(related='order_id.type_sdp',
                              string='Tipo de SdP', readonly=True,
                              store=True)
    sdp_sequence = fields.Char(related='order_id.sdp_sequence',
                              string='Secuencia SdP', track_visibility='onchange', readonly=True,
                              store=True)
    type_order = fields.Selection(related='order_id.type_order',
                              string='Tipo de Orden', readonly=True,
                              store=True)
    order_sequence = fields.Char(related='order_id.order_sequence',
                              string='Secuencia Orden', track_visibility='onchange', readonly=True,
                              store=True)
    #type_sequence = fields.Char(compute='_get_type_sequence', string='Codigo Orden', track_visibility='onchange', store=True)
    product_supplier_id = fields.Many2one('product.supplierinfo', string ="Detalle Proveedor", 
                                track_visibility="onchange")
    delay = fields.Integer(string='Tiempo Entrega Referencial', related='product_supplier_id.delay')
    product_code = fields.Char(string='Codigo Producto Proveedor', related='product_supplier_id.product_code', store=True)
    code_product_supplier_id = fields.Char(string='Codigo Interno Producto Proveedor', related='product_supplier_id.code_product_id')
    name_product_supplier_id = fields.Char(string='Nombre Producto Proveedor', related='product_supplier_id.product_name')
    product_brand_id = fields.Many2one('product.brand', related='product_id.product_brand_id', string='Marca')
    apu_ids = fields.Many2one('project.apu',
                              string='Partida')
    task_ids = fields.Many2one('project.task',
                              string='EDT', track_visibility='onchange')
    code_project = fields.Char('Codigo Proyecto', related='order_id.code_project', store=True)
    adq_type = fields.Selection('Tipo de Adquisicion', related='order_id.adq_type', store=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor', related='order_id.partner_id', store=True)
    code_pa = fields.Char(string='Proveedor', related='order_id.code_pa', store=True)
    status_supplier = fields.Selection(related='order_id.status_supplier')
    currency_id = fields.Many2one('res.currency',string='Moneda', related='order_id.currency_id', store=True)
    quotation_id = fields.Char('Cotizacion', size=30, track_visibility='onchange')
    quotation_link = fields.Char('Link Cotizacion', size=30, track_visibility='onchange')
    cost_type = fields.Selection ([('Materiales','Materiales'), ('Equipo','Equipo'),('Herramienta','Herramienta'), ('Licencia','Licencia'), 
                                    ('Servicios de terceros','Servicios de terceros'),('Flete','Flete'),('Planilla TIT','Planilla TIT')])
    location_supplier = fields.Char('Lugar de Entrega Proveedor', related='order_id.location_supplier', track_visibility='onchange')
    buyer = fields.Selection(related='order_id.buyer')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', related='order_id.payment_term_id')
    date_due = fields.Date(string='Due Date Header', related='order_id.date_due')
    payment_days = fields.Integer(string='Plazo de Pago Cabecera', related='order_id.payment_days')
    edit_payment = fields.Boolean(string='Editar Fecha de Pago')
    
    date_order_line = fields.Date(string='Fecha de Emision de OC', compute='_get_date_order_line', store=True)
    quotation_id = fields.Char('Cotizacion', size=30, track_visibility='onchange')
    quotation_link = fields.Char('Link Cotizacion', size=30, track_visibility='onchange')
    time_obra = fields.Integer('Tiempo Envío Obra', size=4, required=False)
    date_due_line = fields.Date(string='Fecha de Pago', track_visibility='onchange', compute='_get_date_payment', store=True)
    payment_days_line = fields.Integer(string='Plazo de Pago', size=2)

    #@api.multi
    @api.onchange('date_start_up','time_obra')
    def onchange_date_planned(self):
        if not self.date_start_up:
            self.date_planned = False
        else:
            DATETIME_FORMAT = '%Y-%m-%d'
            date_su = datetime.strptime(self.date_start_up, DATETIME_FORMAT)
            lt_days = timedelta(days=self.time_obra) - timedelta(days=1)
            self.date_planned = date_su - lt_days
        return {}

    @api.one
    @api.depends('date_start_up','payment_days_line', 'time_obra')
    def _get_date_payment(self):
        DATETIME_FORMAT = '%Y-%m-%d'
        date_rd = datetime.strptime(self.date_start_up, DATETIME_FORMAT)
        if self.payment_days_line > self.time_obra:
            payment_days = timedelta(days=self.payment_days_line) - timedelta(days=self.time_obra) 
            self.date_due_line = date_rd + payment_days
        elif self.payment_days_line < self.time_obra:
            payment_days = timedelta(days=self.time_obra) - timedelta(days=self.payment_days_line) 
            self.date_due_line = date_rd - payment_days
        elif self.payment_days_line == self.time_obra:
            self.date_due_line = date_rd

    @api.one
    @api.depends('date_start_up', 'delay', 'time_obra')
    def _get_date_order_line(self):
        DATETIME_FORMAT = '%Y-%m-%d'
        date_su = datetime.strptime(self.date_start_up, DATETIME_FORMAT)
        #date_final = date_su.date()
        lt_days = timedelta(days=self.delay) + timedelta(days=self.time_obra) #- timedelta(days=0.5)
        self.date_order_line = date_su - lt_days
    
    """@api.one
    @api.depends('order_id.date_due', 'order_id.payment_days')
    def _get_date_due(self):
        if not self.edit_payment:
            self.date_due = self.order_id.date_due
            self.payment_days = self.order_id.payment_days
        else:
            time_due = self.payment_days
            due_days = timedelta(days=time_due)
            self.date_due = self.date_planned + due_days"""

    """@api.multi
    def _buscar_marcas(self):
        obj = self.env['product.brand'].search([()])
        #obj = self.pool.get('product.brand')
        #ids = obj.search([('name', 'in', self.product_brand_ids)]) 
        #resultado = obj.read(['id','name'])

        #convertimos a una lista de tuplas
        res = []
        for record in obj:
            #creamos la tupla interna
            rec = {}
            #convertimos a cadena el ID para crear la tupla
            rec ['id'] = record.id
            rec ['name'] = record.name
            #agregamos a tupla final
            res.append(product)"""

    """
    @api.multi
    @api.depends('type_order', 'order_sequence')
    def _get_type_sequence(self):
        res = []
        for element in self:
            name = ''
            name += str(element.type_order)
            name += str(element.order_sequence)
            res.append((element, name))
        return res
        """
    """
    @api.one
    @api.depends('order_id')
    def _get_type_order(self):
        for rec in self.order_id:
            self.type_order = rec.type_order

    @api.one
    @api.depends('order_id')
    def _get_order_sequence(self):
        for rec in self.order_id:
            self.order_sequence = rec.order_sequence
    """
    @api.depends('discount')
    def _compute_amount(self):
        for line in self:
            price_unit = False
            # This is always executed for allowing other modules to use this
            # with different conditions than discount != 0
            price = line._get_discounted_price_unit()
            if price != line.price_unit:
                # Only change value if it's different
                price_unit = line.price_unit
                line.price_unit = price
            super(PurchaseOrderLine, line)._compute_amount()
            if price_unit:
                line.price_unit = price_unit

    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
    )

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    @api.multi
    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super(PurchaseOrderLine, self)._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price
