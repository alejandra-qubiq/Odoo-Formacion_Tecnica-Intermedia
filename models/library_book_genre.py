# Copyright 2024 Alejandra García <alejandra.gracia@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class LibraryBookGenre(models.Model):
    _name = "library.book.genre"
    _description = "Model that registers book's genres"

    # Genre name
    name = fields.Char(
        string="Genre"
    )
