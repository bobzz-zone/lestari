# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WorkOrderPotong(Document):
	# def on_submit(self):
	@frappe.whitelist()
	def cari_pohon(self):		
		cari_doc = frappe.db.sql("""
		SELECT
		nthkoc.berat_cor,
		nthkoc.nomor_base_karet,
		nthkoc.kadar,
		dplr.mul_karet,
		dplr.no_spk,
		dplr.qty
		FROM `tabNTHKO Cor` nthkoc
		JOIN `tabNTHKO Cor Detail` nthkocd ON nthkocd.parent = nthkoc.name
		JOIN `tabData Pohon Lilin Resep` dplr ON dplr.parent = nthkoc.pohon_id
		WHERE nthkoc.pohon_id = '{}'
		""".format(self.pohon_id), as_dict = 1)

		for cari in cari_doc:
			self.nomor_base_karet = cari.nomor_base_karet
			self.kadar = cari.kadar
			self.berat_pohon = cari.berat_cor
			baris_baru = {
				'produk_id':cari.mul_karet,
				'no_spk':cari.no_spk,
				'qty':cari.qty
			}
			self.append('tabel_potong',baris_baru)
	# pass
