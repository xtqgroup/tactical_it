    # -*- coding: utf-8 -*-
# © 2009 NetAndCo (<http://www.netandco.net>).
# © 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>
# © 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2018 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models, _ , SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'code_sequence asc'

    product_brand_model_id = fields.Many2one(
        'product.brand.model',
        string='Modelo',
        help='Seleccionar un Modelo para el Productsroducto')
    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        help='Select a brand for this product'
    )
    code_category = fields.Char(related='categ_id.code_final', string='Codigo Categoría')
    code_sequence = fields.Char(string='Codigo Secuencial', store=True, size=2)
    code_final = fields.Char(
        'Codigo Final', compute='_compute_code_finality',
        store=True, readonly=False)

    @api.model
    def default_get(self, fields_list):
        res = super(ProductTemplate, self).default_get(fields_list)
        product = self.env['product.template'].search([('name', '=', self.name)], limit=1)
        res.update({'code_sequence': len(self._context.get('product_template_ids', [])) + 1})
        return res

    @api.depends('code_sequence', 'categ_id.code_final')
    def _compute_code_finality(self):
        for sequence in self:
            if sequence.categ_id:
                sequence.code_final = '%s00%s1' % (sequence.categ_id.code_final, sequence.code_sequence)
            else:
                sequence.code_final = '%s0%s0' % (sequence.categ_id.code_final, sequence.code_sequence)

    @api.multi
    def name_get(self):
        res = super(ProductTemplate, self).name_get()
        res2 = []
        for name_tuple in res:
            product = self.browse(name_tuple[0])
            if not product.product_brand_id:
                res2.append(name_tuple)
                continue
            res2.append((
                name_tuple[0],
                u' {} ({})'.format(name_tuple[1], product.product_brand_id.name)
            ))
        return res2

class ProductProduct(models.Model):
    _inherit = "product.product"

    sequence = fields.Integer(string='Secuencia', size=2)

    @api.multi
    def name_get(self):
        res = super(ProductProduct, self).name_get()
        res2 = []
        for name_tuple in res:
            product = self.browse(name_tuple[0])
            if not product.product_brand_id:
                res2.append(name_tuple)
                continue
            res2.append((
                name_tuple[0],
                u'[{}] {} ({})'.format(product.code_final, name_tuple[1], product.product_brand_id.name)
            ))
        return res2


class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char('Nombre de Marca', required=True)
    description = fields.Text('Descripción', translate=True)
    logo = fields.Binary('Logo')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Seleccionar la empresa dueña de la Marca. OJO: No distribuidor',
        ondelete='restrict'
    )

    @api.multi
    @api.depends('product_ids')
    def _get_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)

    @api.multi
    def name_get(self):
        res = []
        for element in self:
            name = element.name
            res.append((element.id, name))
        return res



class ProductBrandModel(models.Model):
    _name = 'product.brand.model'

    name = fields.Char('Nombre de Modelo', required=True)
    description = fields.Text('Descripción', translate=True)
    brand_id = fields.Many2many(
        'product.brand',
        string='Marca',
        help='Seleccionar la Marca',
        ondelete='restrict'
        )
    product_ids = fields.One2many(
        'product.template',
        'product_brand_model_id',
        string='Model Products',
    )


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _parent_name = "parent_id"
    _parent_store = True

    code_category = fields.Char(
        string='Código de Categoría',
        help='Código para Concatenar',
        store=True,
        size=2
    )
    code_final = fields.Char(
        'Codigo Final', compute='_compute_code_final',
        store=True)

    product_template_ids = fields.One2many('product.template', 'categ_id', string='Lista de Productos')


    @api.model
    def default_get(self, fields_list):
        res = super(ProductCategory, self).default_get(fields_list)
        res.update({'code_category': len(self._context.get('child_id', [])) + 1})
        return res

    @api.constrains('child_id')
    def _check_order_lines_sequence(self):
        all_sequences = self.child_id.mapped('code_category')
        sequences = list(set(all_sequences))
        if len(all_sequences) != len(sequences):
            raise ValidationError(
                _('La secuencia debe ser unica por Categoría!') + ".\n" +
                _('Las siguientes secuencias ya se encuentran en uso') + ":\n" +
                str(sequences))

    @api.depends('code_category', 'parent_id.code_final')
    def _compute_code_final(self):
        for sequence in self:
            if sequence.parent_id:
                if sequence.parent_id.parent_id.parent_id and len(sequence.code_category) == 1:
                    sequence.code_final = '%s0%s' % (sequence.parent_id.code_final, sequence.code_category)
                else:
                    sequence.code_final = '%s%s' % (sequence.parent_id.code_final, sequence.code_category)
            else:
                sequence.code_final = sequence.code_category


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    #_order = 'intern_code asc'

    intern_code = fields.Integer(string='Codigo Interno', size=2, translate=True)

    code_product_id = fields.Char(related='product_tmpl_id.code_final', string='Codigo Interno Producto')
    #product_brand_id = fields.Char(related='product_tmpl_id.product_brand_id', string='Codigo Interno Producto')

    """@api.model
    def default_get(self, fields_list):
        res = super(ProductSupplierinfo, self).default_get(fields_list)
        res.update({'intern_code': len(self._context.get('seller_ids', [])) + 1})
        return res"""

    """product_brand_id = fields.Many2one(
        'product.brand',
        string='Marca',
        help='Elegir una Marca para el Proveedor. Si el Proveedor tiene varias Marcas, realizar un registro por cada uno',
    )"""
    """product_brand_name = fields.Char(
        'Nombre de Marca', related='product_brand_id.name', store=True
        )"""
    #product_type = fields.Selection(related='product_id.type', store=True, string='Tipo de Producto') 
    #product_categ_id = fields.Many2one('product.category', 'Categoria Interna', related='product_id.categ_id', store=True)

    @api.multi
    def name_get(self):
        res = []
        for element in self:
            name = str(element.product_code)
            name += '-'
            name += str(element.product_name)
            res.append((element.id, name))
        return res
