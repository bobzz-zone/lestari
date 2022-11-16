# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UpdateBundleStock(Document):
	def on_submit(self):
		ste = frappe.new_doc("Stock Entry")
		# frappe.msgprint(str(ste))
		ste.stock_entry_type = "Material Transfer"
		ste.employee_id = self.pic
		ste.remarks = self.keterangan
		ste.update_bundle_stock_no = self.name
		for items in self.items:
			baris_baru = {
				'item_code' : items.item,
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.warehouse,
				'qty' : items.qty_penambahan,
				'allow_zero_valuation_rate' : 1
			}
			ste.append("items",baris_baru)
		ste.flags.ignore_permissions = True
		ste.save()
		frappe.msgprint(str(frappe.get_last_doc("Stock Entry")))

