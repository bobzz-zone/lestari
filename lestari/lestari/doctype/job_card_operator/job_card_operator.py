# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class JobCardOperator(Document):
	# def on_submit(self):
	# 	target_doc = frappe.new_doc("Form Hasil Job Card")
	# 	list_ukuran = []
	# 	data = frappe._dict({
	# 		'kadar': "",
	# 		'qty': 0
	# 	})
	# 	for row in sorted(self.tabel_cor, key = lambda i:(i.kadar, i.ukuran_jenis_sprue)):		
	# 		if data.kadar == "":
	# 			data.kadar = row.kadar
	# 		if data.kadar == row.kadar:
	# 			baris_baru = {

	# 			}
	# 			data.qty += 1
	# 		else:
	# 			list_ukuran.append(frappe._dict({
	# 						"kadar": data.kadar,							
	# 						"qty": data.qty
	# 					}))
	# 			data.kadar = row.kadar				
	# 			data.qty = 1

	# 	list_ukuran.append(frappe._dict({
	# 						"kadar": data.kadar,
	# 						"qty": data.qty
	# 					}))

	@frappe.whitelist()
	def simpan_material(self):
		# source_doc = frappe.get_doc("Job Card Operator", self)
		for row in self.tabel_cor:
			if row.no_pohon == self.no_pohon:
				row.batch_cb_1 = self.batch_cb_1
				row.berat_batch_1 = self.berat_batch_1
				row.batch_cb_2 = self.batch_cb_2
				row.berat_batch_2 = self.berat_batch_2
				row.batch_cb_3 = self.batch_cb_3
				row.berat_batch_3 = self.berat_batch_3
		self.pohon_id = ""
		self.no_pohon = ""
		self.batch_cb_1 = ""
		self.berat_batch_1 = 0
		self.batch_cb_2 = ""
		self.berat_batch_2 = 0
		self.batch_cb_3 = ""
		self.berat_batch_3 = 0