# Copyright 2024 Alejandra García <alejandra.gracia@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api


class LibraryBookComponentLine(models.Model):
    _name = "library.book.component.line"
    _description = "Model that registers book's components"

    name = fields.Char(
        string="Packs",
        required=True
    )
    pack_type = fields.Selection(
        string="Type",
        selection=[
            ('collection', 'Collection'),
            ('saga', 'Saga')],
        default="collection"
    )
    book_id = fields.One2many(
        'book.library',
        string='Books',
        ondelete='cascade',
        inverse_name='pack_ids'
    )

    @api.onchange('book_id')
    def _onchange_pack_type(self):
        if not self.pack_type:
            self.pack_type = 'collection'
