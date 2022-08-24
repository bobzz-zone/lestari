# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class NTHKOLilin(Document):
	pass
	# def on_submit(self):
	# 	target_doc = frappe.get_doc('Data Pohon Lilin', self.pohon_id)
	# 	target_doc.warehouse = "Supermarket - L"
	# 	target_doc.nomor_base_karet = self.nomor_base_karet
	# 	target_doc.ukuran_base_karet = self.ukuran_base_karet
	# 	target_doc.sprue_utama = self.sprue_utama
	# 	baris_baru = {
	# 			"warehouse": "Supermarket - L",
	# 			"nomor_nthko": self.name
	# 		}
	# 	target_doc.append("lokasi",baris_baru)
	# 	target_doc.flags.ignore_permission = True
	# 	target_doc.save()
