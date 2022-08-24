# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormHasilWorkOrder(Document):
	@frappe.whitelist()
	def add_reparasi(self):
		baris_baru = {
			"produk_id":self.produk_id,
			"qty":self.qty_bagus,
			"batu_lepas":self.batu_lepas,
			"batu_pecah":self.batu_pecah,
			"keropos":self.qty_keropos,
			"rusak":self.qty_rusak
			}
		self.append('tabel_potong', baris_baru)
		self.qty_bagus=0
		self.qty_rusak=0
		self.batu_pecah=0
		self.qty_keropos=0
		self.batu_lepas=0
