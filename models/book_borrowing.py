# Copyright 2019 Alejandra Garcia  <alejandra.garcia@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BookBorrowing(models.Model):
    _name = 'book.borrowing'

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name="res.partner",
        domain="[('partner', '=', True)]"
    )
    partner_number = fields.Char(
        string='Library Partner Code',
        related="partner_id.partner_number"
    )
    book_id = fields.Many2one(
        string='Book',
        comodel_name='book.library',
        string='Book'
    )
    state = fields.Selection(
        string='State',
        selection=[('borrowed', 'Borrowed'), ('returned', 'Returned')],
        default="borrowed",
        readonly=True,
    )
    borrow_date = fields.Datetime(
        string="Borrow Date",
        default=fields.Datetime.now()
    )
    return_date = fields.Datetime(
        string="Returned Date"
    )

    @api.constrains('book_id')
    def check_book_type(self):
        for rec in self:
            if rec.book_id and rec.book_id.type != 'printed':
                raise ValidationError("Only printed books can be borrowed")

    def return_book(self):
        for rec in self:
            rec.write({'return_date': fields.Datetime.now(),
                       'state': 'returned'})

    @api.model_create_multi
    def create(self, vals):
        if 'book_id' in vals:
            book_id = self.env['book.library'].browse(vals.get('book_id'))
            book_id.is_borrowed = True
            if book_id.qty_available == 0:
                raise ValidationError(
                    "You don't enough quantity to borrow this book"
                )
        return super().create(vals)
