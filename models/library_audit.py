# Copyright 2024 Alejandra García <alejandra.gracia@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class LibraryAudit(models.Model):
    _name = 'library.audit'
    _description = 'Model that recirds library audits'

    operation = fields.Selection(
        selection=[('create', 'create'),
                   ('write', 'write'),
                   ('unlink', 'unlink')],
    )
    date = fields.Datetime(
        string='Date'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User'
    )
    book_id = fields.Many2one(
        comodel_name='book.library',
        string='Book',
    )
