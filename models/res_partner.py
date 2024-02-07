# Copyright 2024 Alejandra García <alejandra.gracia@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_sales = fields.Float(
        compute='_compute_total_sales',
        compute_sudo=True,
        string='Total Sales',
        store=False
    )
    borrowed_books_count = fields.Integer(
        compute="_compute_borrowed"
    )
    borrowed_books = fields.Many2many(
        'book.borrowing',
        string='Borrowed Books',
        store=False,
        compute="_compute_borrowed"
    )
    never_borrowed = fields.Many2many(
        'book.library',
        compute="_compute_never_borrowed",
        string='Never Borrowed Books',
        store=False
    )

    first_name = fields.Char(
        compute='_compute_full_name',
        readonly=False, store=True
    )
    last_name = fields.Char(
        compute='_compute_full_name',
        readonly=False, store=True
    )

    partner = fields.Boolean(
        string='Library partner'
    )
    author = fields.Boolean(
        string="Author"
    )
    partner_number = fields.Char(
        string='Membership number: '
    )
    genre_ids = fields.Many2many(
        comodel_name='library.book.genre',
        relation='res_partner_book_genre_rel',
        column1='partner_id',
        column2='genre_id',
        string='Genres',
    )
    _sql_constraints = [
        ('partner_number_unique',
         'unique (partner_number,company_id)',
         'The Library Partner Code of contact must be unique per company !'
        )
    ]
    author_books_ids = fields.One2many(
        'book.library',
        'author_id',
        string='Books'
    )

    def singup(self):
        self.write({'partner': True})

    def signout(self):
        self.write({'partner': False,
                    'partner_number': False})

    def unlink(self):
        for rec in self:
            if rec.partner:
                if self.env['book.borrowing'].search(
                    [('partner_id', '=', rec.id),
                     ('state', '=', 'borrowed')]):
                    raise UserError(
                        "The partner %s still has books to return" % rec.name)
        return super().unlink()

    @api.depends('name')
    def _compute_full_name(self):
        for record in self:
            if record.name:
                record.first_name = record.name.split(' ')[0]
                record.last_name = record.name.split(' ')[1]
                return record

    @api.onchange('first_name', 'last_name')
    def _onchange_first_last_name(self):
        if not self.first_name or not self.last_name:
            self.name = ''
        else:
            self.name = f'{self.first_name} {self.last_name}'

    def _compute_never_borrowed(self):
        books = self.env['book.library']
        for partner in self:
            never_borrowed = books.search([('author_id', '=', partner.id),
                                           ('is_borrowed', '=', False)])
            partner.never_borrowed = never_borrowed

    @api.depends('borrowed_books')
    def _compute_borrowed(self):
        borrowed = self.env['book.borrowing'].read_group(
            domain=[('partner_id', 'in', self.ids),
                    ('state', '=', 'borrowed')],
            fields=['partner_id'],
            groupby=['partner_id']
        )
        mapped_loans = {
            data['partner_id'][0]: data['partner_id_count']
            for data in borrowed
        }
        for partner in self:
            partner.borrowed_books_count = mapped_loans.get(partner.id, 0)
            partner.borrowed_books = self.env['book.borrowing'].search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'borrowed')]
            )

    def action_view_borrowed_books(self):
        return {
            'name': 'Borrowed Books',
            'type': 'ir.actions.act_window',
            'res_model': 'book.borrowing',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
        }

    def action_view_borrowed_books_from_partner(self):
        return {
            'name': 'Borrowed Books From Author',
            'type': 'ir.actions.act_window',
            'res_model': 'book.library',
            'view_mode': 'tree,form',
            'domain': [('author_id', '=', self.id),
                       ('is_borrowed', '=', True)]
        }

    @api.depends('author_books_ids')
    def _compute_total_sales(self):
        for author in self:
            author.total_sales = sum(author.author_books_ids.mapped(lambda book: book.price * book.qty_borrowed))
