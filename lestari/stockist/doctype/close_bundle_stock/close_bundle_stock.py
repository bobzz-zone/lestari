# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CloseBundleStock(Document):
	@frappe.whitelist()
	def add_row_action(self):
		baris_baru = {
      				"kadar":self.kadar,
                	"sub_kategori":self.category,
                   	"kategori":frappe.get_doc('Item Group',self.category).parent_item_group,
                    "qty_penambahan":self.bruto,
                    "item":frappe.get_value("Item", {'item_group': self.category,'kadar':self.kadar})
                    }
		self.append("items",baris_baru)
		self.kadar = ""
		self.category = ""
		self.bruto = ""
