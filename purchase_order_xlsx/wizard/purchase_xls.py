# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import xlwt
import datetime
import unicodedata
import base64
import io
from io import StringIO
import csv
# import cStringIO
from datetime import datetime
from odoo import api, fields, models, _ , SUPERUSER_ID


class PurchaseReportOut(models.Model):        
    _name = 'purchase.report.out'
    _description = 'purchase order report'
    
    purchase_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Purchase Excel Report', readonly=True)
    purchase_work = fields.Char('Name', size=256)
    file_names = fields.Binary('Purchase CSV Report', readonly=True)
    
   
class WizardWizards(models.Model):        
    _name = 'wizard.reports'
    _description = 'purchase wizard'
    
#purchase order excel report button actions               
    @api.multi
    def action_purchase_report(self):          
#XLS report         
        custom_value = {}
        label_lists=['PO','POR','CLIENTREF','BARCODE','DEFAULTCODE','NAME','QTY','VENDORPRODUCTCODE','TITLE', 'PARTNERNAME', 'EMAIL', 'PHONE', 'MOBILE', 'STREET', 'STREET2', 'ZIP', 'CITY', 'COUNTRY']                    
        order = self.env['purchase.order'].browse(self._context.get('active_ids', list()))      
        workbook = xlwt.Workbook()                      
        for rec in order:              
            purchase = []                                                          
            for line in rec.order_line:                              
                product = {}                                                                       
                product ['product_id'] = line.product_id.name                                                                            
                product ['product_qty'] = line.product_qty                            
                product ['qty_received'] = line.qty_received                           
                product ['qty_invoiced'] = line.qty_invoiced                                              
                product ['price_unit'] = line.price_unit                        
                product ['taxes_id'] = line.taxes_id.name                      
                product ['price_subtotal'] = str(line.price_subtotal)+' '+line.currency_id.symbol                        
                purchase.append(product)
                                                                                           
            custom_value['products'] = purchase               
            custom_value ['partner_id'] = rec.partner_id.name
            custom_value ['partner_ref'] = rec.partner_ref
            custom_value ['payment_term_id'] = rec.payment_term_id.name
            custom_value ['date_order'] = rec.date_order
            custom_value ['partner_no'] = rec.name
            custom_value ['type_order'] = str(rec.type_order)
            custom_value ['order_sequence'] = str(rec.order_sequence)
            custom_value ['code_sdp'] = str(rec.type_sdp)+'-'+str(rec.sdp_sequence)
            custom_value ['amount_total'] = rec.currency_id.symbol+' '+str(rec.amount_total)
            custom_value ['amount_untaxed'] = rec.currency_id.symbol+' '+str(rec.amount_untaxed)
            custom_value ['amount_tax'] = rec.currency_id.symbol+' '+str(rec.amount_tax)
                                                  
            style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz right;', num_format_str='#,##0.00')
            style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour white;align: horiz center;', num_format_str='#,##0.00')
            style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour white;', num_format_str='#,##0.00')         
            style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
            style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
            style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
            style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
            style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
            
                          
            sheet = workbook.add_sheet(rec.name)
            
            sheet.write_merge(2, 3, 1, 2, 'Orden N°', style2)
            #sheet.write_merge(2, 3, 4, 5, custom_value['partner_no'], style2)
            sheet.write_merge(2, 3, 3, 3, custom_value['type_order'], style2) 
            sheet.write_merge(2, 3, 4, 5, custom_value['order_sequence'], style2)      
            sheet.write(5, 1, 'Proveedor', style3)
            sheet.write(5, 2, custom_value['partner_id'], style0)     
            sheet.write_merge(5, 5, 8, 9, 'Fecha Entrega Proveedor', style3)
            sheet.write_merge(5, 5, 10, 11, custom_value['date_order'], style0)     
            sheet.write_merge(6, 6, 8, 9, 'Codigo de SdP', style3)
            sheet.write_merge(6, 6, 10, 11, custom_value['code_sdp'], style0)
            sheet.write_merge(7, 7, 8, 9, 'Condición de Pago', style3)
            sheet.write_merge(7, 7, 10, 11, custom_value['payment_term_id'], style0)

            sheet.write(10, 1, 'Id', style1)                           
            sheet.write_merge(10, 10, 2, 4, 'Producto', style1)
            sheet.write_merge(10, 10, 5, 6, 'Cantidad', style1)        
            sheet.write_merge(10, 10, 7, 8, 'Precio Unitario', style1)
            sheet.write_merge(10, 10, 9, 10, 'Impuestos', style1) 
            sheet.write(10, 11, 'Subtotal', style1)
            
            n = 11; i = 1
            for product in custom_value['products']:
                sheet.write(n, 1, i, style5)  
                sheet.write_merge(n, n, 2, 3, product['product_id'], style6)      
                sheet.write_merge(n, n, 4, 5, product['product_qty'], style0)
                sheet.write_merge(n, n, 6, 7, product['price_unit'], style0)
                sheet.write_merge(n, n, 8, 10, product['taxes_id'], style0)
                sheet.write(n, 11, product['price_subtotal'], style0)                          
                n += 1; i += 1
            sheet.write_merge(n+1, n+1, 9, 10, 'Untaxed Amount', style7)
            sheet.write(n+1, 11, custom_value['amount_untaxed'], style4)
            sheet.write_merge(n+2, n+2, 9, 10, 'Taxes', style7)
            sheet.write(n+2, 11, custom_value['amount_tax'], style4)
            sheet.write_merge(n+3, n+3, 9, 10, 'Total', style7)
            sheet.write(n+3, 11, custom_value['amount_total'], style4)
#CSV report
        datas = []
        for values in order:
            for value in values.order_line:
                if value.product_id.seller_ids:
                    item = [
                            str(value.order_id.name or ''),
                            str(''),
                            str(''),                            
                            str(value.product_id.barcode or ''),
                            str(value.product_id.default_code or ''),
                            str(value.product_id.name or ''),
                            str(value.product_qty or ''),
                            str(value.product_id.seller_ids[0].product_code or ''),
                            str(value.partner_id.title or ''),
                            str(value.partner_id.name or ''),
                            str(value.partner_id.email or ''),
                            str(value.partner_id.phone or ''),
                            str(value.partner_id.mobile or ''),
                            str(value.partner_id.street or ''),
                            str(value.partner_id.street2 or ''),
                            str(value.partner_id.zip or ''),
                            str(value.partner_id.city or ''),
                            str(value.partner_id.country_id.name or ' '),                        
                            ] 
                    datas.append(item)    
        
        output = StringIO()        
        label = (';'.join(label_lists))               
        output.write(label)         
        output.write("\n")   
        
        for data in datas:       
            record = ';'.join(data)           
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(),"utf-8"))
                              
        filename = ('Reporte de Compras'+ '.xls')
        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)                                                 
                       
# Files actions         
        attach_vals = {
                'purchase_data': 'Reporte Compras'+ '.xls',
                'file_name': out,
                'purchase_work':'Purchase'+ '.csv',
                'file_names':data,
            } 
            
        act_id = self.env['purchase.report.out'].create(attach_vals)
        fp.close()
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.report.out',
        'res_id': act_id.id,
        'view_type': 'form',
        'view_mode': 'form',
        'context': self.env.context,
        'target': 'new',
        }

class PurchaseReportOut(models.Model):        
    _name = 'purchase.line.report.out'
    _description = 'Reporte Comparativo Compras'
    
    purchase_data = fields.Char('Nombre', size=256)
    file_name = fields.Binary('Reporte Comparativo Excel', readonly=True)    
   
class WizardWizards(models.Model):        
    _name = 'wizard.line.reports'
    _description = 'Asistente de Reporte de Compras'

    id_project = fields.Many2one('project.project', string='Selección de Proyecto', size=32, required=False)
    code_project = fields.Char('Código de Proyecto', related='id_project.code_project_project', track_visibility='onchange', readonly= True)
    id_pa = fields.Many2one('sprogroup.purchase.request', string='Título de PA', size=20)
    adq_code = fields.Char('Codigo de PA', related='id_pa.code', track_visibility='onchange', readonly=True)
    adq_type = fields.Selection([('Bienes', 'Bienes'), ('Servicio', 'Servicio'), ('Contrato', 'Contrato')])
    all_check_project = fields.Boolean(string='Todos los proyectos', default=True)
    all_check_adq = fields.Boolean(string='Todas las Adquisiciones', default=True)
    all_check_date = fields.Boolean(string='Todas las Fechas', default=True)
    product_id = fields.Many2one('product.template', string='Producto')
    active_product = fields.Boolean(related='product_id.active')
    fe_inicio = fields.Date('Fecha Inicio', track_visibility='onchange')
    fe_final = fields.Date('Fecha Fin', track_visibility='onchange')

#purchase order excel report button actions               
    @api.multi
    def action_purchase_report(self):          
#XLS report         
        custom_value = {}
        current_user_id = self.env['res.users'].browse(self.env.uid)
        label_lists=['PO','POR','CLIENTREF','BARCODE','DEFAULTCODE','NAME','QTY','VENDORPRODUCTCODE','TITLE', 'PARTNERNAME', 'EMAIL', 'PHONE', 'MOBILE', 'STREET', 'STREET2', 'ZIP', 'CITY', 'COUNTRY']                    
        code_project = self.code_project
        adq_code = self.adq_code
        adq_type = self.adq_type
        fe_inicio = self.fe_inicio
        fe_final = self.fe_final

        if self.all_check_project:
            if self.all_check_adq:
                order_pa = self.env['sprogroup.purchase.request.line'].search([('active_product', '=', True)]) 
                order_sdp = self.env['purchase.order.line'].search([('active_product', '=', True), ('state', '=', 'draft')])
                order_oc = self.env['purchase.order.line'].search([('active_product', '=', True), ('state', '=', 'purchase')])
            else:
                order_pa = self.env['sprogroup.purchase.request.line'].search([('adq_type', '=', adq_type), ('active_product', '=', True)]) 
                order_sdp = self.env['purchase.order.line'].search([('adq_type', '=', adq_type), ('state', '=', 'draft')])
                order_oc = self.env['purchase.order.line'].search([('active_product', '=', True), ('state', '=', 'purchase')])
        elif self.all_check_adq:
            order_pa = self.env['sprogroup.purchase.request.line'].search([('code_project', '=', code_project), ('active_product', '=', True)]) 
            order_sdp = self.env['purchase.order.line'].search([('code_project', '=', code_project), ('active_product', '=', True), ('state', '=', 'draft')])
            order_oc = self.env['purchase.order.line'].search([('active_product', '=', True), ('state', '=', 'purchase')])
        else:
            order_pa = self.env['sprogroup.purchase.request.line'].search([('code_project', '=', code_project), ('adq_type', '=', adq_type), ('active_product', '=', True)]) 
            order_sdp = self.env['purchase.order.line'].search([('code_project', '=', code_project), ('adq_type', '=', adq_type), ('active_product', '=', True), ('state', '=', 'draft')])
            order_oc = self.env['purchase.order.line'].search([('active_product', '=', True), ('state', '=', 'purchase')])


        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Reporte', cell_overwrite_ok=True)                      
        style0 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz right;', num_format_str='#,##0.00')
        style1 = xlwt.easyxf('font: name Times New Roman bold on; pattern: pattern solid, fore_colour white;align: horiz center;', num_format_str='#,##0.00')
        style2 = xlwt.easyxf('font:height 400,bold True; pattern: pattern solid, fore_colour white;', num_format_str='#,##0.00')         
        style3 = xlwt.easyxf('font:bold True;', num_format_str='#,##0.00')
        style4 = xlwt.easyxf('font:bold True;  borders:top double;align: horiz right;', num_format_str='#,##0.00')
        style5 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz center;', num_format_str='#,##0')
        style6 = xlwt.easyxf('font: name Times New Roman bold on;', num_format_str='#,##0.00')
        style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')

        
        n = 11; i = 0
        j = 2
        m = 11
        o = 11

        #HEADER PLANIFICACION                           
        sheet.write_merge(10, 10, j, j, 'Codigo Planificación', style1)
        sheet.write_merge(10, 10, j+1, j+1, 'Fecha Planificación', style1)        
        sheet.write_merge(10, 10, j+2, j+3, 'Título', style1)
        sheet.write_merge(10, 10, j+4, j+4, 'Tipo de Adquisición', style1)
        sheet.write_merge(10, 10, j+5, j+5, 'Codigo Proyecto', style1) 
        sheet.write_merge(10, 10, j+6, j+6, 'Realizado por', style1) 
        sheet.write_merge(10, 10, j+7, j+8, 'Proveedor', style1)
        sheet.write_merge(10, 10, j+9, j+9, 'Status Proveedor', style1) 
        sheet.write_merge(10, 10, j+10, j+10, 'Moneda', style1) 
        sheet.write_merge(10, 10, j+11, j+11, 'Criticidad', style1) 
        sheet.write_merge(10, 10, j+12, j+12, 'Codigo Interno', style1) 
        sheet.write_merge(10, 10, j+13, j+13, 'Cantidad', style1)
        sheet.write_merge(10, 10, j+14, j+14, 'UdM', style1)
        sheet.write_merge(10, 10, j+15, j+15, 'Código Producto', style1) 
        sheet.write_merge(10, 10, j+16, j+17, 'Descripción', style1) 
        sheet.write_merge(10, 10, j+18, j+18, 'Marca', style1) 
        sheet.write_merge(10, 10, j+19, j+19, 'Precio Unitario', style1)
        sheet.write_merge(10, 10, j+20, j+20, 'Subtotal', style1) 
        sheet.write_merge(10, 10, j+21, j+21, 'Pago Proyectado', style1)
        sheet.write_merge(10, 10, j+22, j+22, 'Lead Time', style1)
        sheet.write_merge(10, 10, j+23, j+23, 'Fecha Puesta Obra', style1)
        sheet.write_merge(10, 10, j+24, j+24, 'Fecha SolPed', style1)
        sheet.write_merge(10, 10, j+25, j+25, 'Fecha Emision OC', style1)
        sheet.write_merge(10, 10, j+26, j+26,'Fecha Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+27, j+27, 'Fecha Pago', style1)
        sheet.write_merge(10, 10, j+28, j+28, 'Link Cotización', style1)
        sheet.write_merge(10, 10, j+29, j+29, 'Partida', style1) 
        sheet.write_merge(10, 10, j+30, j+30, 'EDT', style1)
        sheet.write_merge(10, 10, j+31, j+31, 'Condición de Pago', style1)
        sheet.write_merge(10, 10, j+32, j+32, 'Cotización', style1)
        sheet.write_merge(10, 10, j+33, j+33, 'Tipo de Costo', style1)
        sheet.write_merge(10, 10, j+34, j+34, 'Lugar Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+35, j+35, 'Comprador', style1)

        #HEADER SOLPED                         
        sheet.write_merge(10, 10, j+36, j+36, 'Codigo SolPed', style1)
        sheet.write_merge(10, 10, j+37, j+37, 'Fecha SolPed', style1)        
        sheet.write_merge(10, 10, j+38, j+39, 'Proveedor', style1)
        sheet.write_merge(10, 10, j+40, j+40, 'Status Proveedor', style1) 
        sheet.write_merge(10, 10, j+41, j+41, 'Moneda', style1) 
        sheet.write_merge(10, 10, j+42, j+42, 'Codigo Interno', style1) 
        sheet.write_merge(10, 10, j+43, j+43, 'Cantidad', style1)
        sheet.write_merge(10, 10, j+44, j+44, 'UdM', style1)
        sheet.write_merge(10, 10, j+45, j+45, 'Código Producto', style1) 
        sheet.write_merge(10, 10, j+46, j+47, 'Descripción', style1) 
        sheet.write_merge(10, 10, j+48, j+48, 'Marca', style1) 
        sheet.write_merge(10, 10, j+49, j+49, 'Precio Unitario', style1)
        sheet.write_merge(10, 10, j+50, j+50, 'Subtotal', style1) 
        sheet.write_merge(10, 10, j+51, j+51, 'Pago Proyectado', style1)
        sheet.write_merge(10, 10, j+52, j+52, 'Lead Time Proveedor', style1)
        sheet.write_merge(10, 10, j+53, j+53, 'Fecha Puesta Obra', style1)
        sheet.write_merge(10, 10, j+54, j+54, 'Fecha Emision OC', style1)
        sheet.write_merge(10, 10, j+55, j+55,'Fecha Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+56, j+56, 'Fecha Pago', style1)
        sheet.write_merge(10, 10, j+57, j+57, 'Link Cotización', style1)
        sheet.write_merge(10, 10, j+58, j+58, 'Partida', style1) 
        sheet.write_merge(10, 10, j+59, j+59, 'EDT', style1)
        sheet.write_merge(10, 10, j+60, j+60, 'Condición de Pago', style1)
        sheet.write_merge(10, 10, j+61, j+61, 'Cotización', style1)
        sheet.write_merge(10, 10, j+62, j+62, 'Tipo de Costo', style1)
        sheet.write_merge(10, 10, j+63, j+63, 'Lugar Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+64, j+64, 'Comprador', style1)   

        #HEADER OC/OS/CTIT                         
        sheet.write_merge(10, 10, j+65, j+65, 'Codigo SolPed', style1)
        sheet.write_merge(10, 10, j+66, j+66, 'Fecha SolPed', style1)        
        sheet.write_merge(10, 10, j+67, j+68, 'Proveedor', style1)
        sheet.write_merge(10, 10, j+69, j+69, 'Status Proveedor', style1) 
        sheet.write_merge(10, 10, j+70, j+70, 'Moneda', style1) 
        sheet.write_merge(10, 10, j+71, j+71, 'Codigo Interno', style1) 
        sheet.write_merge(10, 10, j+72, j+72, 'Cantidad', style1)
        sheet.write_merge(10, 10, j+73, j+73, 'UdM', style1)
        sheet.write_merge(10, 10, j+74, j+74, 'Código Producto', style1) 
        sheet.write_merge(10, 10, j+75, j+76, 'Descripción', style1) 
        sheet.write_merge(10, 10, j+77, j+77, 'Marca', style1) 
        sheet.write_merge(10, 10, j+78, j+78, 'Precio Unitario', style1)
        sheet.write_merge(10, 10, j+79, j+79, 'Subtotal', style1) 
        sheet.write_merge(10, 10, j+80, j+80, 'Pago Proyectado', style1)
        sheet.write_merge(10, 10, j+81, j+81, 'Lead Time Proveedor', style1)
        sheet.write_merge(10, 10, j+82, j+82, 'Fecha Puesta Obra', style1)
        sheet.write_merge(10, 10, j+83, j+83, 'Fecha Emision OC', style1)
        sheet.write_merge(10, 10, j+84, j+84,'Fecha Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+85, j+85, 'Fecha Pago', style1)
        sheet.write_merge(10, 10, j+86, j+86, 'Link Cotización', style1)
        sheet.write_merge(10, 10, j+87, j+87, 'Partida', style1) 
        sheet.write_merge(10, 10, j+88, j+88, 'EDT', style1)
        sheet.write_merge(10, 10, j+89, j+89, 'Condición de Pago', style1)
        sheet.write_merge(10, 10, j+90, j+90, 'Cotización', style1)
        sheet.write_merge(10, 10, j+91, j+91, 'Tipo de Costo', style1)
        sheet.write_merge(10, 10, j+92, j+92, 'Lugar Entrega Proveedor', style1)
        sheet.write_merge(10, 10, j+93, j+93, 'Comprador', style1)

        #CAPTURA DATOS PLANIFICACION
        for rec in order_pa: 
                                                                                                   
            custom_value ['adq_code'] = rec.adq_code
            custom_value ['create_date'] = rec.create_date
            custom_value ['adq_title'] = rec.adq_title
            custom_value ['adq_type'] = str(rec.adq_type)
            custom_value ['code_project'] = rec.code_project
            custom_value ['requested_by'] = rec.requested_by.name
            custom_value ['supplier_id'] = rec.supplier_id.name
            custom_value ['status_supplier'] = str(rec.status_supplier)
            custom_value ['currency_id'] = rec.currency_id.name
            custom_value ['criticality_adq'] = str(rec.criticality_adq)
            custom_value ['code_product_id'] = rec.code_product_id
            custom_value ['product_qty'] = rec.product_qty
            custom_value ['product_uom_id'] = rec.product_uom_id.name  
            custom_value ['product_code'] = rec.product_code
            custom_value ['name'] = rec.name
            custom_value ['product_brand_id'] = rec.product_brand_id.name
            custom_value ['unit_price_ref'] = rec.unit_price_ref 
            custom_value ['subtotal'] = rec.currency_id.symbol+' '+str(rec.subtotal) 
            custom_value ['forecast_payment'] = rec.currency_id.symbol+' '+str(round(rec.forecast_payment)) 
            custom_value ['p_delay'] = rec.p_delay
            custom_value ['p_start_up'] = rec.p_start_up
            custom_value ['p_date_request'] = rec.p_date_request
            custom_value ['p_date_order'] = rec.p_date_order
            custom_value ['date_required'] = rec.date_required
            custom_value ['p_date_payment'] = rec.p_date_payment
            custom_value ['quotation_link'] = rec.quotation_link
            custom_value ['apu_ids'] = str(rec.apu_ids.complete_name) + '-' + str(rec.apu_ids.name)
            custom_value ['task_ids'] = str(rec.task_ids.complete_name) + '-' + str(rec.task_ids.name)
            custom_value ['p_payment_condition'] = rec.p_payment_condition
            custom_value ['quotation_id'] = rec.quotation_id
            custom_value ['cost_type'] = str(rec.cost_type)
            custom_value ['location_supplier'] = rec.location_supplier
            custom_value ['buyer'] = str(rec.buyer)              
                                   
            #ARMADO CUERPO PLANIFICACION                     
            sheet.write_merge(n, n, 2, 2, custom_value ['adq_code'], style6)
            sheet.write_merge(n, n, 3, 3, custom_value ['create_date'], style0)        
            sheet.write_merge(n, n, 4, 5, custom_value ['adq_title'], style0)
            sheet.write_merge(n, n, 6, 6, custom_value ['adq_type'], style0)
            sheet.write_merge(n, n, 7, 7, custom_value ['code_project'], style0) 
            sheet.write_merge(n, n, 8, 8, custom_value ['requested_by'], style0) 
            sheet.write_merge(n, n, 9, 10, custom_value ['supplier_id'], style0)
            sheet.write_merge(n, n, 11, 11, custom_value ['status_supplier'], style0) 
            sheet.write_merge(n, n, 12, 12, custom_value ['currency_id'], style0) 
            sheet.write_merge(n, n, 13, 13, custom_value ['criticality_adq'], style0) 
            sheet.write_merge(n, n, 14, 14, custom_value ['code_product_id'], style0) 
            sheet.write_merge(n, n, 15, 15, custom_value ['product_qty'], style0)
            sheet.write_merge(n, n, 16, 16, custom_value ['product_uom_id'], style0)
            sheet.write_merge(n, n, 17, 17, custom_value ['product_code'], style0)
            sheet.write_merge(n, n, 18, 19, custom_value ['name'], style0)
            sheet.write_merge(n, n, 20, 20, custom_value ['product_brand_id'], style0)
            sheet.write_merge(n, n, 21, 21, custom_value ['unit_price_ref'], style0)
            sheet.write_merge(n, n, 22, 22, custom_value ['subtotal'], style0)
            sheet.write_merge(n, n, 23, 23, custom_value ['forecast_payment'], style0)
            sheet.write_merge(n, n, 24, 24, custom_value ['p_delay'], style0)
            sheet.write_merge(n, n, 25, 25, custom_value ['p_start_up'], style0)
            sheet.write_merge(n, n, 26, 26, custom_value ['p_date_request'], style0)
            sheet.write_merge(n, n, 27, 27, custom_value ['p_date_order'], style0)
            sheet.write_merge(n, n, 28, 28, custom_value ['date_required'], style0)
            sheet.write_merge(n, n, 29, 29, custom_value ['p_date_payment'], style0)
            sheet.write_merge(n, n, 30, 30, custom_value ['quotation_link'], style0)
            sheet.write_merge(n, n, 31, 31, custom_value ['apu_ids'], style0)
            sheet.write_merge(n, n, 32, 32, custom_value ['task_ids'], style0)
            sheet.write_merge(n, n, 33, 33, custom_value ['p_payment_condition'], style0)
            sheet.write_merge(n, n, 34, 34, custom_value ['quotation_id'], style0)
            sheet.write_merge(n, n, 35, 35, custom_value ['cost_type'], style0)
            sheet.write_merge(n, n, 36, 36, custom_value ['location_supplier'], style0)
            sheet.write_merge(n, n, 37, 37, custom_value ['buyer'], style0)

        #n = 10; i = 0 
            n += 1; i += 1  

            #DENTRO DE PLANIFICACION, CAPTURA DE DATOS SOLPED
            code_pa = rec.adq_code
            order_sdp_final = order_sdp.search([('code_pa', '=', code_pa), ('state', '=', 'draft')])
            for rec in order_sdp_final:
                            
                custom_value ['code_sdp'] = str(rec.sdp_sequence)
                custom_value ['create_date'] = rec.create_date
                custom_value ['partner_id'] = rec.partner_id.name
                custom_value ['status_supplier'] = str(rec.status_supplier)
                custom_value ['currency_id'] = rec.currency_id.name
                custom_value ['code_product_id'] = rec.code_product_id
                custom_value ['product_qty'] = rec.product_qty
                custom_value ['product_uom'] = rec.product_uom.name
                custom_value ['product_code'] = rec.product_code
                custom_value ['name'] = rec.name
                custom_value ['product_brand_id'] = rec.product_brand_id.name
                custom_value ['price_unit'] = rec.price_unit 
                custom_value ['price_subtotal'] = rec.currency_id.symbol+' '+str(rec.price_subtotal) 
                custom_value ['forecast_payment'] = rec.currency_id.symbol+' '+str(rec.price_subtotal + rec.price_tax) #AVERIGUAR COMO SE GENERA PRICE_TAX 
                custom_value ['delay'] = rec.delay
                custom_value ['p_start_up'] = rec.date_start_up
                custom_value ['date_order'] = rec.date_order
                custom_value ['date_planned'] = rec.date_planned
                custom_value ['date_due'] = rec.date_due
                custom_value ['quotation_link'] = rec.quotation_link
                custom_value ['apu_ids'] = str(rec.apu_ids.complete_name) + '-' + str(rec.apu_ids.name)
                custom_value ['task_ids'] = str(rec.task_ids.complete_name) + '-' + str(rec.task_ids.name)
                custom_value ['payment_term_id'] = rec.payment_days_line
                custom_value ['quotation_id'] = rec.quotation_idcell_overwrite_ok=True
                custom_value ['cost_type'] = str(rec.cost_type)
                custom_value ['location_supplier'] = rec.location_supplier
                custom_value ['buyer'] = str(rec.buyer)             
            
                #BODY
                j=38                         
                sheet.write_merge(m, m, j, j, custom_value ['code_sdp'], style6)
                sheet.write_merge(m, m, j+1, j+1, custom_value ['create_date'], style0)         
                sheet.write_merge(m, m, j+2, j+3, custom_value ['partner_id'], style0) ##
                sheet.write_merge(m, m, j+4, j+4, custom_value ['status_supplier'], style0) 
                sheet.write_merge(m, m, j+5, j+5, custom_value ['currency_id'], style0) 
                sheet.write_merge(m, m, j+6, j+6, custom_value ['code_product_id'], style0) 
                sheet.write_merge(m, m, j+7, j+7, custom_value ['product_qty'], style0)
                sheet.write_merge(m, m, j+8, j+8, custom_value ['product_uom'], style0)
                sheet.write_merge(m, m, j+9, j+9, custom_value ['product_code'], style0)
                sheet.write_merge(m, m, j+10, j+11, custom_value ['name'], style0) ##
                sheet.write_merge(m, m, j+12, j+12, custom_value ['product_brand_id'], style0)
                sheet.write_merge(m, m, j+13, j+13, custom_value ['price_unit'], style0)
                sheet.write_merge(m, m, j+14, j+14, custom_value ['price_subtotal'], style0)
                sheet.write_merge(m, m, j+15, j+15, custom_value ['forecast_payment'], style0)
                sheet.write_merge(m, m, j+16, j+16, custom_value ['delay'], style0)
                sheet.write_merge(m, m, j+17, j+17, custom_value ['p_start_up'], style0)
                sheet.write_merge(m, m, j+18, j+18, custom_value ['date_order'], style0)
                sheet.write_merge(m, m, j+19, j+19, custom_value ['date_planned'], style0)
                sheet.write_merge(m, m, j+20, j+20, custom_value ['date_due'], style0)
                sheet.write_merge(m, m, j+21, j+21, custom_value ['quotation_link'], style0)
                sheet.write_merge(m, m, j+22, j+22, custom_value ['apu_ids'], style0)
                sheet.write_merge(m, m, j+23, j+23, custom_value ['task_ids'], style0)
                sheet.write_merge(m, m, j+24, j+24, custom_value ['payment_term_id'], style0)
                sheet.write_merge(m, m, j+25, j+25, custom_value ['quotation_id'], style0)
                sheet.write_merge(m, m, j+26, j+26, custom_value ['cost_type'], style0)
                sheet.write_merge(m, m, j+27, j+27, custom_value ['location_supplier'], style0)
                sheet.write_merge(m, m, j+28, j+28, custom_value ['buyer'], style0)    

                m += 1; i += 1 

                code_sdp = rec.sdp_sequence
                if self.fe_inicio and self.fe_final:
                    order_oc_final = order_oc.search([('sdp_sequence', '=', code_sdp), ('state', '=', 'purchase'), ('create_date', '>=', fe_inicio), ('create_date', '<=', fe_final)])
                elif self.all_check_date:
                    order_oc_final = order_oc.search([('sdp_sequence', '=', code_sdp), ('state', '=', 'purchase')])

                for rec in order_oc_final:
                                
                    custom_value ['code_order'] = str(rec.order_sequence)
                    custom_value ['create_date'] = rec.create_date
                    custom_value ['partner_id'] = rec.partner_id.name
                    custom_value ['status_supplier'] = str(rec.status_supplier)
                    custom_value ['currency_id'] = rec.currency_id.name
                    custom_value ['code_product_id'] = rec.code_product_id
                    custom_value ['product_qty'] = rec.product_qty
                    custom_value ['product_uom'] = rec.product_uom.name
                    custom_value ['product_code'] = rec.product_code
                    custom_value ['name'] = rec.name
                    custom_value ['product_brand_id'] = rec.product_brand_id.name
                    custom_value ['price_unit'] = rec.price_unit 
                    custom_value ['price_subtotal'] = rec.currency_id.symbol+' '+str(rec.price_subtotal) 
                    custom_value ['forecast_payment'] = rec.currency_id.symbol+' '+str(rec.price_subtotal + rec.price_tax) #AVERIGUAR COMO SE GENERA PRICE_TAX 
                    custom_value ['delay'] = rec.delay
                    custom_value ['p_start_up'] = rec.date_start_up
                    custom_value ['date_order'] = rec.date_order
                    custom_value ['date_planned'] = rec.date_planned
                    custom_value ['date_due'] = rec.date_due
                    custom_value ['quotation_link'] = rec.quotation_link
                    custom_value ['apu_ids'] = str(rec.apu_ids.complete_name) + '-' + str(rec.apu_ids.name)
                    custom_value ['task_ids'] = str(rec.task_ids.complete_name) + '-' + str(rec.task_ids.name)
                    custom_value ['payment_term_id'] = rec.payment_days_line
                    custom_value ['quotation_id'] = rec.quotation_idcell_overwrite_ok=True
                    custom_value ['cost_type'] = str(rec.cost_type)
                    custom_value ['location_supplier'] = rec.location_supplier
                    custom_value ['buyer'] = str(rec.buyer)             
                
                    #BODY
                    j=67                         
                    sheet.write_merge(o, o, j, j, custom_value ['code_order'], style6)
                    sheet.write_merge(o, o, j+1, j+1, custom_value ['create_date'], style0)         
                    sheet.write_merge(o, o, j+2, j+3, custom_value ['partner_id'], style0) ##
                    sheet.write_merge(o, o, j+4, j+4, custom_value ['status_supplier'], style0) 
                    sheet.write_merge(o, o, j+5, j+5, custom_value ['currency_id'], style0) 
                    sheet.write_merge(o, o, j+6, j+6, custom_value ['code_product_id'], style0) 
                    sheet.write_merge(o, o, j+7, j+7, custom_value ['product_qty'], style0)
                    sheet.write_merge(o, o, j+8, j+8, custom_value ['product_uom'], style0)
                    sheet.write_merge(o, o, j+9, j+9, custom_value ['product_code'], style0)
                    sheet.write_merge(o, o, j+10, j+11, custom_value ['name'], style0) ##
                    sheet.write_merge(o, o, j+12, j+12, custom_value ['product_brand_id'], style0)
                    sheet.write_merge(o, o, j+13, j+13, custom_value ['price_unit'], style0)
                    sheet.write_merge(o, o, j+14, j+14, custom_value ['price_subtotal'], style0)
                    sheet.write_merge(o, o, j+15, j+15, custom_value ['forecast_payment'], style0)
                    sheet.write_merge(o, o, j+16, j+16, custom_value ['delay'], style0)
                    sheet.write_merge(o, o, j+17, j+17, custom_value ['p_start_up'], style0)
                    sheet.write_merge(o, o, j+18, j+18, custom_value ['date_order'], style0)
                    sheet.write_merge(o, o, j+19, j+19, custom_value ['date_planned'], style0)
                    sheet.write_merge(o, o, j+20, j+20, custom_value ['date_due'], style0)
                    sheet.write_merge(o, o, j+21, j+21, custom_value ['quotation_link'], style0)
                    sheet.write_merge(o, o, j+22, j+22, custom_value ['apu_ids'], style0)
                    sheet.write_merge(o, o, j+23, j+23, custom_value ['task_ids'], style0)
                    sheet.write_merge(o, o, j+24, j+24, custom_value ['payment_term_id'], style0)
                    sheet.write_merge(o, o, j+25, j+25, custom_value ['quotation_id'], style0)
                    sheet.write_merge(o, o, j+26, j+26, custom_value ['cost_type'], style0)
                    sheet.write_merge(o, o, j+27, j+27, custom_value ['location_supplier'], style0)
                    sheet.write_merge(o, o, j+28, j+28, custom_value ['buyer'], style0) 

                    o += 1; i += 1 

                m = o 

            n = m 
        #n = 10; i = 0 
                              
        filename = ('Reporte de Compras'+ '.xls')
        workbook.save(filename)
        #UNICO COMENTARIO EN EL REMOTO
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data) 

# Files actions         
        attach_vals = {
                'purchase_data': 'Reporte Compras'+ '.xls',
                'file_name': out,
                    } 
            
        act_id = self.env['purchase.line.report.out'].create(attach_vals)
        fp.close()
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.line.report.out',
        'res_id': act_id.id,
        'view_type': 'form',
        'view_mode': 'form',
        'context': self.env.context,
        'target': 'new',
        }
 




















