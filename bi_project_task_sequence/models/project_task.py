# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _ , SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class ProjectApu(models.Model):
    _inherit = 'project.apu'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence_name'
    #_rec_name = 'complete_name'
    _order = 'parent_left'

    sequence_name = fields.Char("Sequence", store=True, size=2)
    sequence_parent = fields.Char(string='Codigo Padre', related='parent_id.sequence_name', store=True, track_visibility='always')
    #sequence_parent_id = fields.Many2one('project.apu', 'Secuencia Padre', index=True, ondelete='cascade')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    apu_level = fields.Integer('Nivel de Partida', store=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('sequence_name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for sequence in self:
            if sequence.parent_id:
                sequence.complete_name = '%s.0%s' % (sequence.parent_id.complete_name, sequence.sequence_name)
            else:
                sequence.complete_name = sequence.sequence_name     
    
    @api.model
    def default_get(self, fields_list):
        res = super(ProjectApu, self).default_get(fields_list)
        res.update({'sequence_name': len(self._context.get('child_ids', [])) + 1})
        return res

    @api.multi
    def name_get(self):
        res = []
        for element in self:
            name = str(element.complete_name)
            name += '-'
            name += str(element.name)
            res.append((element.id, name))
        return res

    """@api.depends('apu_level')
    @api.model
    def create(self,vals):
        #for rec in self:
        if vals['apu_level'] == 2:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus2')
        elif vals['apu_level'] == 1:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus')
        elif vals['apu_level'] == 3:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus3')
        elif vals['apu_level'] == 4:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus4')
        elif vals['apu_level'] == 5:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus5')
        elif vals['apu_level'] == 6:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus6')
        elif vals['apu_level'] == 7:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.apus7')
        return super(project_apu, self).create(vals)"""

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _parent_name = "sequence_parent_id"
    _parent_store = True
    _parent_order = 'sequence_name'
    #_rec_name = 'complete_name'
    _order = 'parent_left'

    sequence_name = fields.Char("Sequence", readonly=True, store=True)
    sequence_parent = fields.Char(string='Codigo Padre', related='parent_id.sequence_name', store=True, track_visibility='always')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    task_level = fields.Integer('Nivel de Tarea', store=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('sequence_name', 'parent_id.complete_name','project_id.sequence')
    def _compute_complete_name(self):
        for sequence in self:
            if sequence.project_id:
                if sequence.parent_id:
                    sequence.complete_name = '%s.0%s' % (sequence.parent_id.complete_name, sequence.sequence_name)
                else:
                    sequence.complete_name = '%s.0%s' % (sequence.project_id.sequence, sequence.sequence_name)
            else:
                 sequence.complete_name = sequence.sequence_name   

    @api.model
    def default_get(self, fields_list):
        res = super(ProjectTask, self).default_get(fields_list)
        res.update({'sequence_name': len(self._context.get('child_ids', [])) + 1})
        return res

    @api.multi
    def name_get(self):
        res = []
        for element in self:
            name = str(element.complete_name)
            name += '-'
            name += str(element.name)
            res.append((element.id, name))
        return res

    """@api.depends('sequence_name', 'project_id.sequence')
    def _compute_complete_name(self):
        for sequence in self:
            if sequence.project_id:
                sequence.complete_name = '%s.0%s' % (sequence.project_id.sequence, sequence.sequence_name)
            else:
                sequence.complete_name = sequence.sequence_name  
    """
    """@api.model
    def default_get(self, fields_list):
        res = super(ProjectTask, self).default_get(fields_list)
        res.update({'sequence_name': len(self._context.get('task_ids', [])) + 1})
        return res"""

    """@api.depends('task_level')
    @api.model
    def create(self,vals):
        if vals['task_level'] == 2:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks2')
        elif vals['task_level'] == 1:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks')
        elif vals['task_level'] == 3:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks3')
        elif vals['task_level'] == 4:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks4')
        elif vals['task_level'] == 5:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks5')
        elif vals['task_level'] == 6:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks6')
        elif vals['task_level'] == 7:
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks7')
        return super(project_task, self).create(vals)"""	
    	
        #if vals.get('sequence_name', _('New')) == _('New') and self.parent_id: #vals.get('parent_id.sequence_name', _('New')) == 'parent_id.sequence_name':
        #	sequence_name = str(vals['parent_id.sequence_name']) + '.' + (self.env['ir.sequence'].next_by_code('project.tasks') or _('New'))
        #	vals['sequence_name'] = sequence_name
            #vals['sequence_name'] = self.env['ir.sequence'].broswe(self.parent_id.sequence_name) + '.' + (self.env['ir.sequence'].next_by_code('project.tasks') or _('New'))
        #if vals.get('sequence_name', _('New')) == _('New'):
        #	sequence_name = self.env['ir.sequence'].next_by_code('project.tasks') or '/' #_('New'))
        #	vals['sequence_name'] = sequence_name
        #elif self.task_level and vals.get('sequence_name', _('New')) == _('New'):
        #	sequence_name = (self.env['ir.sequence'].next_by_code('project.tasks2') or _('New'))
        #	vals['sequence_name'] = sequence_name
        #res = super(project_task, self).create(vals)
        #return res


    """
    @api.depends('parent_id')
    @api.model
    def create(self,vals):
        if vals.get('sequence_name', _('New')) == _('New') and self.parent_id:
        	sequence_name = str(vals[''])
            vals['sequence_name'] = self.env['ir.sequence'].broswe(self.parent_id.sequence_name) + '.' + (self.env['ir.sequence'].next_by_code('project.tasks') or _('New'))
        elif vals.get('sequence_name', _('New')) == _('New'):
        	vals['sequence_name'] = self.env['ir.sequence'].next_by_code('project.tasks') or _('New')
        res = super(project_task, self).create(vals)
        return res
    """

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 