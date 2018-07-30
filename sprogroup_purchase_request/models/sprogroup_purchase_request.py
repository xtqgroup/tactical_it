# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _ , SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
_STATES = [
    ('draft', 'Planificado'),
    ('to_approve', 'Eliminar 1'),
    ('leader_approved', 'Eliminar 2'),
    ('manager_approved', 'Eliminar 3'),
    ('rejected', 'Rechazado'),
    ('done', 'Solicitado')
]


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    id_pa = fields.Many2one('sprogroup.purchase.request', string='Título de PA', size=20, required=True)
    code_project = fields.Char('Código de Proyecto', compute='_get_code_project', store=True)
    code_pa = fields.Char('Código de PA', compute='_get_code_pa')
    adq_type = fields.Selection('Tipo de Adquisicion', related='id_pa.adq_type', store=True, readonly=True)
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

    """
    @api.multi
    def name_get(self):
        result = super(PurchaseOrder, self).name_get()
        res = []
        for element in self:
            name = ''
            name += element.type_order
            name += '-'
            name += element.order_sequence
            res.append((element.id, name))
        return res
    """        
class SprogroupPurchaseRequest(models.Model):

    _name = 'sprogroup.purchase.request'
    _description = 'Sprogroup Purchase Request'
    _inherit = ['mail.thread']

    @api.one
    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.one
    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('sprogroup.purchase.request')

    #@api.multi
    #def _compute_supplier_id(self):
    #    for rec in self:
    #        if rec.product_id:
    #            if rec.product_id.seller_ids:
    #                rec.supplier_id = rec.product_id.seller_ids[0].name

    name = fields.Char('Título',size=34, store=True, required=True,
                        track_visibility='onchange')
    id_project = fields.Many2one('project.project', string='Selección de Proyecto', size=32, required=False)
    id_purchase_order = fields.One2many('purchase.order', 'id_pa', string='Ordenes Relacionadas', store=True)
    #type_sdp = fields.Selection(related='id_purchase_order.type_sdp', string='Tipo de SdP')
    #sdp_sequence = fields.Char(related='id_purchase_order.sdp_sequence', string='SdP Secuencia')
    code_project = fields.Char('Código de Proyecto', compute='_get_code',track_visibility='onchange', store=True)
    #task_ids =fields.Many2many('project.task', string='EDT de Proyecto', compute='_get_task', track_visibility='onchange')
    #component_project =fields.Char('Componente de Proyecto', compute='_get_component',track_visibility='onchange')
    delay_oc = fields.Integer('Lead Time OC', size= 10, required=True, track_visibility='onchange')
    buyer = fields.Selection([('Tactical IT', 'Tactical IT'),('Consorcio', 'Consorcio')])
    supplier_id =fields.Many2one('res.partner',
                                  string='Proveedor')
    location_supplier = fields.Char('Lugar de Entrega Proveedor', size=30, track_visibility='onchange')
    status_supplier = fields.Selection([('Cotizado', 'Cotizado'), ('Seleccionado', 'Seleccionado'), ('Referencial', 'Referencial')])
    adq_type = fields.Selection([('Bienes', 'Bienes'), ('Servicio', 'Servicio'), ('Contrato', 'Contrato')], required=True)
    adq_quotation = fields.Char('Cotización', size=30, track_visibility='onchange')
    criticality_adq = fields.Selection([('Critico', 'Crítico'), ('No Crítico', 'No Crítico'), ('Normal', 'Normal')], string='Criticidad ADQ')
    service_amount = fields.Float('Monto de Servicio', help='Monto de todo el Servicio', track_visibility='onchange')
    advance = fields.Float('Monto de Adelanto', compute='_get_advance', store=True, size=30, track_visibility='onchange')
    advance_percentage = fields.Float('Porcentaje de Adelanto', size=30, track_visibility='onchange')
    advance_date = fields.Date('Fecha de Adelanto', size=30, track_visibility='onchange')
    warranty_percentage = fields.Float('Porcentaje de Garantía', size=30, track_visibility='onchange')
    warranty_date = fields.Date('Fecha de Garantía', size=30, track_visibility='onchange')
    warranty = fields.Float('Monto de Garantía', compute='_get_warranty', store=True, size=30, track_visibility='onchange')

    #Calculo de los montos# 
    @api.multi
    @api.depends('warranty_percentage', 'service_amount')
    def _get_warranty(self): 
        self.warranty = self.warranty_percentage * self.service_amount

    @api.multi
    @api.depends('advance_percentage', 'service_amount')
    def _get_advance(self): 
        self.advance = self.advance_percentage * self.service_amount

    @api.onchange('service_amount', 'warranty_percentage', 'advance_percentage')
    def _get_onchange_amount(self): 
        if self.service_amount:
            self.warranty = self.warranty_percentage * self.service_amount
            self.advance = self.advance_percentage * self.service_amount

    code = fields.Char('Código', size=32, readonly=True,
                       track_visibility='onchange')
    date_start = fields.Date('Fecha de inicio',
                             help="Date when the user initiated the request.",
                             default=fields.Date.context_today,
                             track_visibility='onchange')
    end_start = fields.Date('Fecha de entrega',default=fields.Date.context_today,
                             track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   'Realizado por',
                                   required=False,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    assigned_to = fields.Many2one('res.users', 'Approver',
                                  track_visibility='onchange',
                                  default=_get_default_requested_by)
    description = fields.Text('Description')
    currency_id = fields.Many2one('res.currency','Moneda', required=True, track_visibility='onchange', store=True)
    line_ids = fields.One2many('sprogroup.purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True,
                               track_visibility='onchange')
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')

    @api.one
    @api.depends('id_project')
    def _get_code(self): 
        for rec in self.id_project:
            self.code_project = rec.code_project_project

    @api.one
    @api.depends('id_project')
    def _get_task(self): 
        for rec in self.id_project:
            self.task_ids = rec.task_ids

    @api.onchange('state')
    def onchange_state(self):
        assigned_to = None
        if self.state:
            if (self.requested_by.id == False):
                self.assigned_to = None
                return

            employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
            if(len(employee) > 0):
                if(employee[0].department_id and employee[0].department_id.manager_id):
                    assigned_to = employee[0].department_id.manager_id.user_id

        self.assigned_to =  assigned_to

    @api.one
    @api.depends('requested_by')
    def _compute_department(self):
        if (self.requested_by.id == False):
            self.department_id = None
            return

        employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
        if (len(employee) > 0):
            self.department_id = employee[0].department_id.id
        else:
            self.department_id = None

    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department', store=True,)

    @api.one
    @api.depends('state')
    def _compute_can_leader_approved(self):
        current_user_id = self.env.uid
        if(self.state == 'to_approve' and current_user_id == self.assigned_to.id):
            self.can_leader_approved = True
        else:
            self.can_leader_approved = False
    can_leader_approved = fields.Boolean(string='Can Leader approved',compute='_compute_can_leader_approved')

    @api.one
    @api.depends('state')
    def _compute_can_manager_approved(self):
        current_user = self.env['res.users'].browse(self.env.uid)

        if (self.state == 'leader_approved' and current_user_id == self.assigned_to.id):
            self.can_manager_approved = True
        else:
            self.can_manager_approved = False

    can_manager_approved = fields.Boolean(string='Can Manager approved',compute='_compute_can_manager_approved')

    @api.one
    @api.depends('state')
    def _compute_last_manager_approved(self):
        current_user = self.env['res.users'].browse(self.env.uid)

        if (self.state == 'manager_approved' and current_user_id == self.assigned_to.id):
            self.last_manager_approved = True
        else:
            self.last_manager_approved = False

    last_manager_approved = fields.Boolean(string='Last Manager approved',compute='_compute_last_manager_approved')

    @api.one
    @api.depends('state')
    def _compute_can_reject(self):
        self.can_reject = (self.can_leader_approved or self.can_manager_approved)

    can_reject = fields.Boolean(string='Can reject',compute='_compute_can_reject')



    @api.multi
    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'leader_approved','manager_approved', 'rejected', 'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string="Is editable",
                                 compute="_compute_is_editable",
                                 readonly=True)

    @api.model
    def create(self, vals):
        request = super(SprogroupPurchaseRequest, self).create(vals)
        if vals.get('assigned_to'):
            request.message_subscribe_users(user_ids=[request.assigned_to.id])
        return request

    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('assigned_to'):
                self.message_subscribe_users(user_ids=[request.assigned_to.id])
        return res

    @api.multi
    def button_draft(self):
        self.mapped('line_ids').do_uncancel()
        return self.write({'state': 'draft'})

    @api.multi
    def button_to_approve(self):
        return self.write({'state': 'to_approve'})

    @api.multi
    def button_leader_approved(self):
        return self.write({'state': 'leader_approved'})


    @api.multi
    def button_manager_approved(self):
        return self.write({'state': 'manager_approved'})

    @api.multi
    def button_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    @api.multi
    def button_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({'state': 'rejected'})

    @api.multi
    def make_purchase_quotation(self):
        view_id = self.env.ref('purchase.purchase_order_form')

        #vals = {
            #'id_pa': self.name,
        #    'currency_id': self.currency_id.id,
        #    'partner_id': self.supplier_id.id,
        #    'type_sdp': 'SdB'
        #     'picking_type_id': self.rule_id.picking_type_id.id,
        #     'company_id': self.company_id.id,
        #     'currency_id': partner.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
        #     'dest_address_id': self.partner_dest_id.id,
        #     'origin': self.origin,
        #     'payment_term_id': partner.property_supplier_payment_term_id.id,
        #     'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        #     'fiscal_position_id': fpos,
        #     'group_id': group
        #    }
        """
        currency_id = []
        for line in self:
            currency_line = (0, 0, {'currency_id' : line.currency_id.id
                                    })
            currency_id.append(currency_line)

        id_pa = []
        for line in self:
            pa_line = (0, 0, {'id_pa' : line.id
                                    })
            id_pa.append(pa_line)
            """

        order_line = []
        for line in self.line_ids:
            currency_id = line.currency_id.name
            product = line.product_id
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)

            product_line = (0, 0, {'product_id' : line.product_id.id,
                                   'state' : 'draft',
                                   'product_uom' : line.product_id.uom_po_id.id,
                                    'price_unit' : line.unit_price_ref,
                                    'quotation_id': line.quotation_id,
                                    'time_obra': line.time_obra,
                                    'quotation_link': line.quotation_link,
                                    'cost_type': line.cost_type,
                                    'date_order_line': line.p_date_order,
                                   'date_planned' :  line.date_new, #datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                   #'taxes_id' : ((6,0,[taxes_id.id])),
                                   'product_qty' : line.product_qty,
                                   'date_start_up' : line.p_start_up,
                                   'location_supplier': line.location_supplier,
                                   #'product_supplier_id': line.product_supplier_id.id,
                                   'apu_ids' : line.apu_ids.id, 
                                   'task_ids' : line.task_ids.id,
                                   'status_supplier': line.status_supplier,
                                   'date_due_line': line.p_date_payment,
                                   'payment_days_line': line.p_payment_condition,
                                   #'adq_type': line.adq_type,
                                   'name' : line.product_id.name
                                   })
            order_line.append(product_line)

        # vals = {
        #     'order_line' : order_line
        # }
        #
        #po = self.env['purchase.order'].create(vals)


        return {
            'name': _('New Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'context': {
                'default_order_line': order_line,
                #'default_currency_id': currency_id,
                #'default_id_pa': (1, 0, {self.name}),
                'default_state': 'draft',
                        }
        } 

#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

class SprogroupPurchaseRequestLine(models.Model):

    _name = "sprogroup.purchase.request.line"
    _description = "Sprogroup Purchase Request Line"
    _inherit = ['mail.thread']

    @api.multi
    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty',
                  'date_required', 'specifications')


    @api.multi
    def _compute_supplier_id(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.seller_ids:
                    rec.supplier_id = rec.product_id.seller_ids[0].name

    apu_ids = fields.Many2one('project.apu',
                              string='Partida')
    product_id = fields.Many2one(
        'product.product', 'Producto',
        domain=[('purchase_ok', '=', True)], required=True,
        track_visibility='onchange')
    active_product = fields.Boolean(related='product_id.active', string='Activo Producto')
    code_product_id = fields.Char(string='Codigo Interno Producto' , related='product_id.code_final')
    product_brand_id = fields.Many2one('product.brand', related='product_id.product_brand_id', string='Marca')
    name = fields.Char('Descripción', size=256,
                       track_visibility='onchange')
    p_delay = fields.Integer('Tiempo de Entrega', size=30,
                            track_visibility='onchange')
    p_payment_condition = fields.Integer('Condición de Pago', size=30,
                                          track_visibility='onchange')
    p_start_up = fields.Date('Fecha de Puesta en Obra', store=True, required=True, track_visibility='onchange', default=fields.Date.context_today)
    time_obra = fields.Integer('Tiempo Envío Obra', size=4, required=False)
    p_date_payment = fields.Date('Fecha de Pago', store= True, track_visibility='onchange', compute='_get_date_payment')
    p_date_request = fields.Date('Fecha SolPed', store=True, track_visibility='onchange', compute='_get_date_request')
    p_date_order = fields.Date('Fecha emisión OC', store=True,track_visibility='onchange', compute='_get_date_order')

    subtotal = fields.Float('Subtotal', store=True, compute='_get_subtotal')
    product_uom_id = fields.Many2one('product.uom', 'Product Unit of Measure',
                                     track_visibility='onchange')
    #uom_id = fields.Many2one('product.template', 'Unidad de Medida', track_visibility='onchange')
    quotation_id = fields.Char('Cotizacion', size=30, track_visibility='onchange')
    quotation_link = fields.Char('Link Cotizacion', size=30, track_visibility='onchange')
    cost_type = fields.Selection ([('Materiales','Materiales'), ('Equipo','Equipo'),('Herramienta','Herramienta'), ('Licencia','Licencia'),
                                ('Servicios de terceros','Servicios de terceros'),('Flete','Flete'),('Planilla TIT','Planilla TIT')])
    product_qty = fields.Float('Cantidad', track_visibility='onchange', size=30)
    delay_oc = fields.Integer(related='request_id.delay_oc',
                             string='Lead Time OC', readonly=True,
                             store=True, default=5)
    adq_type = fields.Selection(related='request_id.adq_type',
                             string='Tipo de Adquisicion', track_visibility='onchange', readonly=True,
                             store=True)
    """type_sdp = fields.Selection(related='request_id.type_sdp',
                             string='Tipo SdP', track_visibility='onchange', readonly=True,
                             store=True)
    sdp_sequence = fields.Char(related='request_id.sdp_sequence',
                             string='SdP Secuencia', track_visibility='onchange', readonly=True,
                             store=True)"""
    forecast_payment = fields.Float('Pago Proyectado', track_visibility='onchange', compute='_get_forecast')
    
    #Campo que llama al objeto sprogroup.purchase.request
    request_id = fields.Many2one('sprogroup.purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 store=True, readonly=True)
    buyer = fields.Selection(related='request_id.buyer')
    supplier_id = fields.Many2one('res.partner', string="Proveedor", related='request_id.supplier_id')
    status_supplier = fields.Selection(related='request_id.status_supplier')
    criticality_adq = fields.Selection(related='request_id.criticality_adq', string='Criticidad ADQ')
    #service_amount = fields.Float('Monto de Servicio', related='request_id.service_amount', help='Monto de todo el Servicio', track_visibility='onchange')
    unit_price_ref = fields.Float('Precio Unitario', track_visibility='onchange', compute='_get_unit_price_ref', readonly=False, store=True) #
    warranty = fields.Float('Monto de Garantía', related='request_id.warranty', store=True, size=30, track_visibility='onchange')
    advance = fields.Float('Monto de Adelanto', related='request_id.advance', store=True, size=30, track_visibility='onchange')
    product_supplier_id = fields.Many2one('product.supplierinfo', string ="Detalle Proveedor", track_visibility="onchange")
    #product_brand_id = fields.Many2one('product.brand', related='product_supplier_id.product_brand_id', string='Marca')
    delay = fields.Integer(string='Tiempo Entrega Referencial', related='product_supplier_id.delay')
    product_code = fields.Char(string='Codigo Producto Proveedor', related='product_supplier_id.product_code', store=True)
    code_product_supplier_id = fields.Char(string='Codigo Interno Producto Proveedor', related='product_supplier_id.code_product_id')
    name_product_supplier_id = fields.Char(string='Nombre Producto Proveedor', related='product_supplier_id.product_name')
    location_supplier = fields.Char('Lugar de Entrega Proveedor', related='request_id.location_supplier', track_visibility='onchange')
    date_new = fields.Date('Fecha Entrega', compute='_get_date_new', store=True)

    @api.one
    @api.depends('date_required')
    def _get_date_new(self):
      DATETIME_FORMAT = '%Y-%m-%d'
      date_rd = datetime.strptime(self.date_required,DATETIME_FORMAT)
      lt_days = timedelta(days=1)
      self.date_new = date_rd + lt_days

    @api.one
    #@api.depends('request_id.service_amount', 'adq_type')
    def _get_unit_price_ref(self):
        if not self.adq_type == 'Bienes':
            #for rec in self:   
            self.unit_price_ref = self.request_id.service_amount

    @api.one
    @api.depends('subtotal', 'product_qty', 'warranty', 'advance', 'adq_type')
    def _get_forecast(self):
        if self.adq_type == 'Bienes':
            self.forecast_payment = self.subtotal * 1.18 #Agregar TAX IGV tabla tax_id
        else:
            self.forecast_payment = self.subtotal - ((self.product_qty * self.warranty)+(self.product_qty * self.advance))

    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Realizado por',
                                   store=True, readonly=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True, readonly=True)
    date_start = fields.Date(related='request_id.date_start',
                             string='Fecha de Inicio', readonly=True,
                             store=True)
    end_start = fields.Date(related='request_id.end_start',
                             string='Fecha de Entrega Final', readonly=True,
                             store=True)
    id_project = fields.Many2one('project.project', related='request_id.id_project',
                                string='Nombre Proyecto',
                                readonly=True)
    task_ids = fields.Many2one('project.task',
                              string='EDT', track_visibility='onchange')
    code_project = fields.Char(related='request_id.code_project',
                              string='Codigo Proyecto', readonly=True,
                              store=True)
    adq_title = fields.Char(related='request_id.name',
                              string='Titulo de PA', readonly=True,
                              store=True)
    adq_code = fields.Char(related='request_id.code',
                              string='Código de PA', readonly=True,
                              store=True)
    state = fields.Selection(related='request_id.state',
                            string='Estado de PA', readonly=True,
                            store=True)
    description = fields.Text(related='request_id.description',
                              string='Descripción', readonly=True,
                              store=True)
    date_required = fields.Date(string='Fecha de Entrega Proveedor', required=True, readonly=False,
                                track_visibility='onchange', compute='_get_date_required') #, default=fields.Date.context_today
    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state',
                                     readonly=True,
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    currency_id = fields.Many2one('res.currency',string='Moneda', related='request_id.currency_id', store=True, track_visibility='onchange')
    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False)

    @api.one
    @api.depends('request_id')
    def _get_task(self): 
        #for rec in self.request_id:
        self.task_ids = self.request_id.task_ids

    @api.one
    @api.depends('product_qty','unit_price_ref')
    def _get_subtotal(self):
      self.subtotal = self.product_qty * self.unit_price_ref

    @api.one
    @api.depends('p_start_up','time_obra')
    def _get_date_required(self):
      DATETIME_FORMAT = '%Y-%m-%d'
      date_rd = datetime.strptime(self.p_start_up,DATETIME_FORMAT)
      lt_days = timedelta(days=self.time_obra)
      self.date_required = date_rd - lt_days

    @api.one
    @api.depends('date_required','p_delay','delay_oc')
    def _get_date_request(self):
      DATETIME_FORMAT = '%Y-%m-%d'
      date_rd = datetime.strptime(self.date_required,DATETIME_FORMAT)
      lt_days = timedelta(days=self.p_delay)
      ltoc_days = timedelta(days=self.delay_oc)
      self.p_date_request = date_rd - lt_days - ltoc_days
    
    @api.one
    @api.depends('date_required','p_delay')
    def _get_date_order(self):
      DATETIME_FORMAT = '%Y-%m-%d'
      date_rd = datetime.strptime(self.date_required,DATETIME_FORMAT)
      lt_days = timedelta(days=self.p_delay)
      self.p_date_order = date_rd - lt_days 
    
    @api.one
    @api.depends('date_required','p_payment_condition')
    def _get_date_payment(self):
      DATETIME_FORMAT = '%Y-%m-%d'
      date_rd = datetime.strptime(self.date_required,DATETIME_FORMAT)
      payment_days = timedelta(days=self.p_payment_condition)
      self.p_date_payment = date_rd + payment_days

    """
    @api.onchange('request_id')
    def onchange_request_id(self):
        if self.request_id.code_project:
            self.code_project = self.request_id.code_project
    """
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            #self.product_qty = 1
            self.name = name

    @api.multi
    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({'cancelled': True})

    @api.multi
    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({'cancelled': False})

    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to_approve', 'leader_approved','manager_approved',  'rejected',
                                        'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string='Is editable',
                                 compute="_compute_is_editable",
                                 readonly=True)
    @api.multi
    def write(self, vals):
        res = super(SprogroupPurchaseRequestLine, self).write(vals)
        if vals.get('cancelled'):
            requests = self.mapped('request_id')
            requests.check_auto_reject()
        return res
