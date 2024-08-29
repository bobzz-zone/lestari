# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransferMaterialMasuk(Document):
	def on_submit(self):
		# pass
		new_doc = frappe.new_doc("Stock Entry")
		new_doc.stock_entry_type = "Transfer Material Masuk"
		new_doc.posting_date = self.tanggal_transaksi
		new_doc.append("items",{
			"item_code":self.item,
			"qty":self.qty,
			"warehouse":frappe.db.get_value("Item Default", {"parent":self.item}, "default_warehouse"),
			"targe_warehouse":frappe.db.get_value("Item Default", {"parent":self.item}, "default_target_warehouse")
		})
		frappe.msgprint(str(new_doc))
		new_doc.save()
	# 	self.db_set("stock_entry", new_doc.name)"
