# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PermintaanBatu(Document):
	def on_submit(self):
		new_doc = frappe.new_doc("Material Request")
		new_doc.material_request_type = "Purchase"
		new_doc.idmaterial_request = self.name
		new_doc.employee_id = self.id_employee
		new_doc.employee_name = self.nama_employee
		new_doc.transaction_date = self.posting_date
		new_doc.schedule_date = self.tanggal_dibutuhkan
		new_doc.set_warehouse = "Batu - LMS"
		new_doc.terms = self.catatan
		for row in self.items:
			baris_baru = {
				"item_code" : row.item_code,
				"qty": row.qty
			}
			new_doc.append("items",baris_baru)
		new_doc.flags.ignore_permissions = True
		new_doc.save()
		self.id_material_request = new_doc.name
		new_doc.submit()
