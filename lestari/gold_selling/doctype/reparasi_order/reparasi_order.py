# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ReparasiOrder(Document):
	def on_submit(self):
		ste = frappe.new_doc('Stock Entry')
		ste.stock_entry_type = 'Material Receipt'
		for row in self.items:
			ste.append('items', {
				'item_code': row.item,
				'qty': row.bruto,
				'uom': frappe.db.get_value("Item", row.item, 'stock_uom'),
				't_warehouse': "Reparasi Customer - LMS",
				'conversion_factor': 1,
			})
		ste.flags.ignore_permissions = True
		ste.submit()
