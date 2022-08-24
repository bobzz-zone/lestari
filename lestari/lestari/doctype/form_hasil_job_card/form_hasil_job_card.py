# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormHasilJobCard(Document):
	@frappe.whitelist()
	def cari_job_card(self):
		cari_doc = frappe.db.sql("""
		SELECT
		*
		FROM `tabJob Card Operator` jco
		JOIN `tabJob Card Operator Cor` jcoc ON jcoc.parent = jco.name
		WHERE jco.name = '{}' AND jcoc.kadar = '{}' ORDER BY jcoc.no_pohon DESC
		""".format(self.no_job_card,self.kadar), as_dict = 1)

		for cari in cari_doc:
			baris_baru = {
				'no_pohon':cari.no_pohon,
				'kadar':cari.kadar,
				'material_cor':cari.material_cor,
				'berat':cari.berat,
				'pohon_id':cari.pohon_id,
				'no_spk':cari.no_spk,
				'qty':cari.qty,
				'batch_cb_1':cari.batch_cb_1,
				'batch_cb_2':cari.batch_cb_2,
				'batch_cb_3':cari.batch_cb_3,
				'berat_batch_1':cari.berat_batch_1,
				'berat_batch_2':cari.berat_batch_2,
				'berat_batch_3':cari.berat_batch_3,
				'total_berat_batch':cari.total_berat_batch
			}
			self.append('tabel_cor',baris_baru)
	# pass

@frappe.whitelist()
def get_kadar(doctype, txt, searchfield, start, page_len, filters=None):
	return frappe.db.sql(
	"""SELECT DISTINCT
		jcoc.kadar
		FROM `tabJob Card Operator` jco
		JOIN `tabJob Card Operator Cor` jcoc ON jcoc.parent = jco.name
		WHERE jco.name = '{}' ORDER BY jcoc.name DESC
		""".format(filters.get("parent")), {
		'txt': "%{}%".format(txt),
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})
