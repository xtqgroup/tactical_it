# -*- coding: utf-8 -*-

from odoo import fields, api, models, _ , SUPERUSER_ID


"""class SprogroupPurchaseRequestLine(models.Model):
    _inherit ='sprogroup.purchase.request.line'

    apu_ids = fields.Many2one('project.apu',
                              string='Partida')"""
    
class ProjectTask(models.Model):
    _inherit = 'project.task'

    product_ids = fields.Many2many('product.product', string="Products")
    #prueba = fields.Char('Valor', size=20)
    apu_ids = fields.Many2many('project.apu', string='Partidas Relacionadas')

class ProjectProject(models.Model):
    _inherit = 'project.project'

    code_project_project = fields.Char('Código de Proyecto', size=32)
    #sequence_project = fields.Integer('Secuencia Proyecto', size=2, store=True)
    currency_id = fields.Many2one('res.currency','Moneda')
    component_project_project = fields.Char('Componente de Proyecto', size=30)
    #purchase_request = fields.One2many('sprogroup.purchase.request','id_project')
    amount_project = fields.Float('Monto de Proyecto')
    place_project = fields.Char('Lugar de Proyecto')
    #purchase_order = fields.One2many('purchase.order','id_project')

class ProjectApu(models.Model):
    _name = "project.apu"
    _description = "Partidas"
    _date_name = "date_start"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _mail_post_access = 'read'
    _order = "priority desc, sequence, id desc"

    def _get_default_partner(self):
        if 'default_project_id' in self.env.context:
            default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
            return default_project_id.exists().partner_id

    def _get_default_stage_id(self):
      
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    active = fields.Boolean(default=True)
    name = fields.Char(string='Nombre Partida', track_visibility='always', required=True, index=True)
    description = fields.Html(string='Description')
    task_ids = fields.Many2many('project.task', string='EDT Relacionados', track_visibility='onchange')
    priority = fields.Selection([
                                ('0', 'Low'),
                                ('1', 'Normal'),
                                ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
                            help="Gives the sequence order when displaying a list of tasks.")
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
                                default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                                domain="[('project_ids', '=', project_id)]", copy=False)
    tag_ids = fields.Many2many('project.tags', string='Tags', oldname='categ_ids')
    kanban_state = fields.Selection([
                                    ('normal', 'Grey'),
                                    ('done', 'Green'),
                                    ('blocked', 'Red')], string='Kanban State',
                                    copy=False, default='normal', required=True,
                                    help="A task's kanban state indicates special situations affecting it:\n"
                                         " * Grey is the default situation\n"
                                         " * Red indicates something is preventing the progress of this task\n"
                                         " * Green indicates the task is ready to be pulled to the next stage")
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State', track_visibility='onchange')
    create_date = fields.Datetime(index=True)
    write_date = fields.Datetime(index=True)  #not displayed in the view but it might be useful with base_automation module (and it needs to be defined first for that)
    date_start = fields.Datetime(string='Starting Date',
                                default=fields.Datetime.now,
                                index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
                                            default=fields.Datetime.now,
                                            index=True,
                                            copy=False,
                                            readonly=True)
    project_id = fields.Many2one('project.project',
                                string='Project',
                                default=lambda self: self.env.context.get('default_project_id'),
                                index=True,
                                track_visibility='onchange',
                                change_default=True)
    notes = fields.Text(string='Notes')
    planned_hours = fields.Float(string='Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.')
    remaining_hours = fields.Float(string='Remaining Hours', digits=(16,2), help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    user_id = fields.Many2one('res.users',
                                string='Assigned to',
                                default=lambda self: self.env.uid,
                                index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
                                string='Customer',
                                default=_get_default_partner)
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True, related_sudo=False)
    company_id = fields.Many2one('res.company',
                                string='Company',
                                default=lambda self: self.env['res.company']._company_default_get())
    color = fields.Integer(string='Color Index')
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True, related_sudo=False)
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
                                    help="Attachment that don't come from message.")
                                # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment', domain="[('res_model', '=', 'project.apu'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Cover Image')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    parent_id = fields.Many2one('project.apu', string='Partida Padre', index=True)
    child_ids = fields.One2many('project.apu', 'parent_id', string="Sub-Partidas" ,context={'active_test': False}) #
    #subtask_project_id = fields.Many2one('project.project', related="project_id.subtask_project_id", string='Sub-task Project', readonly=True)
    #subtask_count = fields.Integer(compute='_compute_subtask_count', type='integer', string="Contador SubPartidas")
    email_from = fields.Char(string='Email', help="These people will receive email.", index=True)
    email_cc = fields.Char(string='Watchers Emails')
                        # Computed field about working time elapsed between record creation and assignation/closing.
    working_hours_open = fields.Float(compute='_compute_elapsed', string='Working hours to assign', store=True, group_operator="avg")
    working_hours_close = fields.Float(compute='_compute_elapsed', string='Working hours to close', store=True, group_operator="avg")
    working_days_open = fields.Float(compute='_compute_elapsed', string='Working days to assign', store=True, group_operator="avg")
    working_days_close = fields.Float(compute='_compute_elapsed', string='Working days to close', store=True, group_operator="avg")
    # customer portal: include comment and incoming emails in communication history
    website_message_ids = fields.One2many(domain=lambda self: [('model', '=', self._name), ('message_type', 'in', ['email', 'comment'])])

    def _compute_attachment_ids(self):
        for task in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', task.id), ('res_model', '=', 'project.apu')]).ids
            message_attachment_ids = self.mapped('message_ids.attachment_ids').ids  # from mail_thread
            task.attachment_ids = list(set(attachment_ids) - set(message_attachment_ids))

    @api.multi
    @api.depends('create_date', 'date_end', 'date_assign')
    def _compute_elapsed(self):
        task_linked_to_calendar = self.filtered(
            lambda task: task.project_id.resource_calendar_id and task.create_date
        )
        for task in task_linked_to_calendar:
            dt_create_date = fields.Datetime.from_string(task.create_date)

            if task.date_assign:
                dt_date_assign = fields.Datetime.from_string(task.date_assign)
                task.working_hours_open = task.project_id.resource_calendar_id.get_work_hours_count(
                        dt_create_date, dt_date_assign, False, compute_leaves=True)
                task.working_days_open = task.working_hours_open / 24.0

            if task.date_end:
                dt_date_end = fields.Datetime.from_string(task.date_end)
                task.working_hours_close = task.project_id.resource_calendar_id.get_work_hours_count(
                    dt_create_date, dt_date_end, False, compute_leaves=True)
                task.working_days_close = task.working_hours_close / 24.0

        (self - task_linked_to_calendar).update(dict.fromkeys(
            ['working_hours_open', 'working_hours_close', 'working_days_open', 'working_days_close'], 0.0))

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done
    
    def _compute_portal_url(self):
        super(ProjectApu, self)._compute_portal_url()
        for task in self:
            task.portal_url = '/my/task/%s' % task.id
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.email_from = self.partner_id.email

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id
            if self.project_id not in self.stage_id.project_ids:
                self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.stage_id = False

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Datetime.now()
    """
    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        return super(ProjectApu, self).copy(default)
    """
    #@api.multi
    #def _compute_subtask_count(self):
    #    for task in self:
    #    task.subtask_count = self.search_count([('id', 'child_of', task.id), ('id', '!=', task.id)])
    
    @api.constrains('parent_id')
    def _check_parent_id(self):
        for task in self:
            if not task._check_recursion():
                raise ValidationError(_('Error! You cannot create recursive hierarchy of task(s).'))

    """@api.constrains('parent_id')
    def _check_subtask_project(self):
        for task in self:
            if task.parent_id.project_id and task.project_id != task.parent_id.project_id.subtask_project_id:
                raise UserError(_("You can't define a parent task if its project is not correctly configured. The sub-task's project of the parent task's project should be this task's project"))
    """
    # Override view according to the company definition
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        tm = obj_tm and obj_tm.name or 'Hours'

        res = super(ProjectApu, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        # using get_object to get translation value
        uom_hour = self.env.ref('product.product_uom_hour', False)
        if not obj_tm or not uom_hour or obj_tm.id == uom_hour.id:
            return res

        eview = etree.fromstring(res['arch'])

        # if the project_time_mode_id is not in hours (so in days), display it as a float field
        def _check_rec(eview):
            if eview.attrib.get('widget', '') == 'float_time':
                eview.set('widget', 'float')
            for child in eview:
                _check_rec(child)
            return True

        _check_rec(eview)

        res['arch'] = etree.tostring(eview, encoding='unicode')

        # replace reference of 'Hours' to 'Day(s)'
        for f in res['fields']:
            # TODO this NOT work in different language than english
            # the field 'Initially Planned Hours' should be replaced by 'Initially Planned Days'
            # but string 'Initially Planned Days' is not available in translation
            if 'Hours' in res['fields'][f]['string']:
                res['fields'][f]['string'] = res['fields'][f]['string'].replace('Hours', obj_tm.name)
        return res

    @api.model
    def get_empty_list_help(self, help):
        self = self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=_("tasks")
        )
        return super(ProjectApu, self).get_empty_list_help(help)

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence'):
     
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    # ------------------------------------------------
    # CRUD overrides
    # ------------------------------------------------

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        # Stage change: Update date_end if folded stage
        if vals.get('stage_id'):
            vals.update(self.update_date_end(vals['stage_id']))
        task = super(ProjectApu, self.with_context(context)).create(vals)
        return task

    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id') and 'date_assign' not in vals:
            vals['date_assign'] = now

        result = super(ProjectApu, self).write(vals)

        return result

    def update_date_end(self, stage_id):
        project_task_type = self.env['project.task.type'].browse(stage_id)
        if project_task_type.fold:
            return {'date_end': fields.Datetime.now()}
        return {'date_end': False}

    @api.multi
    def get_access_action(self, access_uid=None):
       
        self.ensure_one()
        user, record = self.env.user, self
        if access_uid:
            user = self.env['res.users'].sudo().browse(access_uid)
            record = self.sudo(user)

        if user.share:
            try:
                record.check_access_rule('read')
            except AccessError:
                pass
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/my/apu/%s' % self.id,
                    'target': 'self',
                    'res_id': self.id,
                }
        return super(ProjectApu, self).get_access_action(access_uid)

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(ProjectApu, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value_ids = tracking[test_task.id]
        if 'stage_id' in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id, {'composition_mode': 'mass_mail'})
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state_label' in init_values and self.kanban_state == 'blocked':
            return 'project.mt_task_blocked'
        elif 'kanban_state_label' in init_values and self.kanban_state == 'done':
            return 'project.mt_task_ready'
        elif 'user_id' in init_values and self.user_id:  # assigned -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values and self.stage_id and self.stage_id.sequence <= 1:  # start stage -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values:
            return 'project.mt_task_stage'
        return super(ProjectApu, self)._track_subtype(init_values)

    @api.multi
    def _notification_recipients(self, message, groups):
       
        groups = super(ProjectApu, self)._notification_recipients(message, groups)

        self.ensure_one()
        if not self.user_id:
            take_action = self._notification_link_helper('assign')
            project_actions = [{'url': take_action, 'title': _('I take it')}]
        else:
            project_actions = []

        new_group = (
            'group_project_user', lambda partner: bool(partner.user_ids) and any(user.has_group('project.group_project_user') for user in partner.user_ids), {
                'actions': project_actions,
            })

        groups = [new_group] + groups
        for group_name, group_method, group_data in groups:
            if group_name in ['customer', 'portal']:
                continue
            group_data['has_button_access'] = True

        return groups

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        #Override to get the reply_to of the parent project.
        tasks = self.sudo().browse(res_ids)
        project_ids = tasks.mapped('project_id').ids
        aliases = self.env['project.project'].message_get_reply_to(project_ids, default=default)
        return {task.id: aliases.get(task.project_id.id, False) for task in tasks}

    @api.multi
    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('project_id.alias_name')
        return [x for x in email_list if x.split('@')[0] not in aliases]

    @api.model
    def message_new(self, msg, custom_values=None):
        # Overrides mail_thread message_new that is called by the mailgateway
        #    through message_process.
        #    This override updates the document according to the email.
        
        # remove default author when going through the mail gateway. Indeed we
        # do not want to explicitly set user_id to False; however we do not
        # want the gateway user to be responsible if no other responsible is
        # found.
        create_context = dict(self.env.context or {})
        create_context['default_user_id'] = False
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id')
        }
        defaults.update(custom_values)

        task = super(ProjectApu, self.with_context(create_context)).message_new(msg, custom_values=defaults)
        email_list = task.email_split(msg)
        partner_ids = [p for p in task._find_partner_from_emails(email_list, force_create=False) if p]
        task.message_subscribe(partner_ids)
        return task

    @api.multi
    def message_update(self, msg, update_vals=None):
        #Override to update the task according to the email. 
        if update_vals is None:
            update_vals = {}
        maps = {
            'cost': 'planned_hours',
        }
        for line in msg['body'].split('\n'):
            line = line.strip()
            res = tools.command_re.match(line)
            if res:
                match = res.group(1).lower()
                field = maps.get(match)
                if field:
                    try:
                        update_vals[field] = float(res.group(2).lower())
                    except (ValueError, TypeError):
                        pass

        email_list = self.email_split(msg)
        partner_ids = [p for p in self._find_partner_from_emails(email_list, force_create=False) if p]
        self.message_subscribe(partner_ids)
        return super(ProjectApu, self).message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(ProjectApu, self).message_get_suggested_recipients()
        for task in self.filtered('partner_id'):
            reason = _('Customer Email') if task.partner_id.email else _('Customer')
            if task.partner_id:
                task._message_add_suggested_recipient(recipients, partner=task.partner_id, reason=reason)
            elif task.email_from:
                task._message_add_suggested_recipient(recipients, partner=task.email_from, reason=reason)
        return recipients

    @api.multi
    def message_get_email_values(self, notif_mail=None):
        res = super(ProjectApu, self).message_get_email_values(notif_mail=notif_mail)
        headers = {}
        if res.get('headers'):
            try:
                headers.update(safe_eval(res['headers']))
            except Exception:
                pass
        if self.project_id:
            current_objects = [h for h in headers.get('X-Odoo-Objects', '').split(',') if h]
            current_objects.insert(0, 'project.project-%s, ' % self.project_id.id)
            headers['X-Odoo-Objects'] = ','.join(current_objects)
        if self.tag_ids:
            headers['X-Odoo-Tags'] = ','.join(self.tag_ids.mapped('name'))
        res['headers'] = repr(headers)
        return res

    def _message_post_after_hook(self, message):
        if self.email_from and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email_from)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email_from', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(ProjectApu, self)._message_post_after_hook(message)

    def action_assign_to_me(self):
        self.write({'user_id': self.env.user.id})

    def action_open_parent_apu(self):
        return {
            'name': _('Parent Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.apu',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window'
        }

    def action_subapu(self):
        action = self.env.ref('project_task_product.project_apu_action_sub_apu').read()[0]
        ctx = self.env.context.copy()
        ctx.update({
            'default_parent_id' : self.id,
            #'default_project_id' : self.env.context.get('project_id', self.subtask_project_id.id),
            'default_name' : self.env.context.get('name', self.name) + ':',
            'default_partner_id' : self.env.context.get('partner_id', self.partner_id.id),
            #'search_default_project_id': self.env.context.get('project_id', self.subtask_project_id.id),
        })
        action['context'] = ctx
        action['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id)]
        return action
        
