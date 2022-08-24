# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class NTHKOPotong(Document):
	def on_submit(self):
		target_doc = frappe.new_doc("Item")
		for row in self.table_detail:
			target_doc.item_code = frappe.get_doc("Item",row.produk_id).name + " Potong"
			target_doc.item_group = frappe.get_doc("Item",row.produk_id).item_group
			target_doc.item_name = frappe.get_doc("Item",row.produk_id).item_name + " Potong"
			target_doc.stock_uom = frappe.get_doc("Item",row.produk_id).stock_uom
			target_doc.kadar = frappe.get_doc("Item",row.produk_id).kadar
			target_doc.qty_isi_pohon = frappe.get_doc("Item",row.produk_id).qty_isi_pohon
			target_doc.brand = frappe.get_doc("Item",row.produk_id).brand
			target_doc.description = frappe.get_doc("Item",row.produk_id).description
			target_doc.is_purchase_item = 0
			target_doc.is_sales_item = 0
			target_doc.flags.ignore_permissions = True
			target_doc.save()



