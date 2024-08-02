# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
from datetime import datetime # from python std library
from frappe.utils import now_datetime , now, getdate
from frappe.utils import flt

class PermintaanBatu(Document):
	#MRB.YY..MM..DD..####
	@frappe.whitelist()
	def autoname(self):
		date = getdate(self.posting_date)
		tahun = date.strftime("%y")
		bulan = date.strftime("%m")
		hari = date.strftime("%d")
		# frappe.throw(str(self.naming_series))
		self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
		self.name = self.naming_series.replace(".####", getseries(self.naming_series,4))

	def on_submit(self):
		# if self.owner != "izzi@lms.com":
		new_doc = frappe.new_doc("Material Request")
		new_doc.material_request_type = "Purchase"
		new_doc.idmaterial_request = self.id_material_request
		new_doc.employee_id = self.employee
		new_doc.employee_erp = self.id_employee
		new_doc.employee_name = self.nama_employee
		new_doc.transaction_date = self.posting_date
		new_doc.schedule_date = self.tanggal_dibutuhkan
		new_doc.jenis_mr = "O" if self.type == "O" else "Non O"
		new_doc.set_warehouse = "Batu - LMS" if self.type == "O" else "Batu Non O - LMS"
		new_doc.jenis_dokumen = "Batu"
		new_doc.department = "Batu - LMS"
		new_doc.terms = self.catatan
		new_doc.from_laravel = 1
		for row in self.items:
			baris_baru = {
				"item_code" : row.item_code,
				"qty": row.qty,
				"proses": "Batu"
			}
			new_doc.append("items",baris_baru)
		new_doc.flags.ignore_permissions = True
		new_doc.save()
		self.id_material_request = new_doc.name
		new_doc.submit()
