# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormKebutuhanMulKaret(Document):
	def on_submit(self):
		target_doc = frappe.new_doc("Stock Entry")
		target_doc.stock_entry_type = "Material Transfer"
		target_doc.remarks = self.name
		for row in self.tabel_mul_karet:
			baris_baru = {
				'item_code': row.mul_karet,
				'qty':1,
				'uom':frappe.get_doc("Item",row.produk_id).stock_uom,
				'convertion_factor':1,
				's_warehouse':frappe.get_doc("Item",row.produk_id).item_defaults[0].default_warehouse,
				't_warehouse':'Work In Progress - L',
				'serial_no':row.mul_karet_id,
				'allow_zero_valuation_rate':1
			}
			target_doc.append('items',baris_baru)
		target_doc.flags.ignore_permission = True
		target_doc.save()

	# pass
