# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today

class RPHGips(Document):
	def on_submit(self):
		sumber_doc = self
		# target_doc1 = frappe.new_doc("Material Request")
		# target_doc1.material_request_type = "Manufacture"
		# target_doc1.schedule_date = add_days(today(),1)
		current_data = sumber_doc.tabel_gips
		sorted_data = []
		sorted_data = sorted(current_data, key = lambda i:(i.kadar, i.nomor_base_karet))

		# for row in sumber_doc.tabel_gips:	
		# 	qty = flt(frappe.get_doc("Data Logam", row.kadar).koefisien) * flt(row.berat_pohon)
		# 	item_name = frappe.get_doc("Item", row.kadar).item_name
		# 	uom = frappe.get_doc("Item", row.kadar).stock_uom
		# 	mr_item = {
		# 		'item_code': row.kadar,
		# 		'item_name': item_name,
		# 		'schedule_date': add_days(today(),1),
		# 		'warehouse': "Campur Bahan - L",
		# 		'uom': uom,
		# 		'qty': qty,
		# 	}
		# 	target_doc1.append("items",mr_item)
		# target_doc1.flags.ignore_permissions = True
		# target_doc1.save()
		# no_mr = target_doc1.name

		target_doc = frappe.new_doc("Work Order Gips")
		for row in sorted_data:

			baris_baru = {
				'no_spk': row.no_spk,
				'nomor_base_karet': row.nomor_base_karet,
				'kadar': row.kadar,
				'tanggal_pohonan': row.tanggal_pohonan,
				'pohon_id': row.pohon_id,
				'ukuran_base_karet': row.ukuran_base_karet,
				'ukuran': row.ukuran,
				'berat_lilin': row.berat_lilin,
				'berat_batu': row.berat_batu,
				'berat_pohon': row.berat_pohon,
				# 'qty_permintaan': row.qty
			}
			target_doc.append("tabel_pohon",baris_baru)

		target_doc.flags.ignore_permissions = True
		target_doc.save()

@frappe.whitelist()
def get_data_gips(from_tanggal = None, to_tanggal = None, kadar = None, jenis_sprue = None):
	data = []
	# data.append({'tanggal_pohonan':tanggal_pohonan,'kadar':kadar,'kategori':kategori,'sub_kategori':sub_kategori})
	condition = ""
	if from_tanggal:
		condition += "AND"+" (fhwo.created_date between '"+from_tanggal+"'"
	if to_tanggal:
		condition += " AND '"+to_tanggal+"')"
	if kadar:
		condition += " AND fhwod.kadar = '"+kadar+"'"
	if jenis_sprue:
		condition += " AND fhwod.jenis_sprue = '"+jenis_sprue+"'"
	frappe.msgprint(condition)
	sumber_nthko = frappe.db.sql("""
	SELECT
	nthkod.no_spk,
	nthkod.nomor_base_karet,
	nthkod.tanggal_pohonan,
	nthkod.pohon_id,
	nthkod.kadar,
	nthkod.qty,
	nthkod.ukuran,
	nthkod.berat_lilin,
	nthkod.berat_batu,
	nthkod.berat_pohon,
	nthkod.ukuran_base_karet
	FROM `tabNTHKO Lilin` nthko
	JOIN `tabNTHKO Lilin Detail` nthkod ON nthkod.parent = nthko.name
	WHERE nthko.docstatus = 1 {}
	""".format(condition),as_dict=1)

	return sumber_nthko

@frappe.whitelist()
def get_items_nthko_lilin(source_name, target_doc=None):
	def update_item(source, target, source_parent):
		target.work_order_id = source_parent.work_order_id

	def set_missing_values(source, target):
		rph = frappe.get_doc(target)
		rph.work_order_id = source.work_order_id
		frappe.msgprint(source.work_order_id)

	doc = get_mapped_doc("NTHKO Lilin", source_name, {
		"NTHKO Lilin": {
			"doctype": "RPH Gips",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"NTHKO Lilin Detail": {
			"doctype": "RPH Gips Detail",
			"field_map": {
				"name": "nthko_lilin_detail",
				"parent": "nthko_lilin"
			},
			"postprocess": update_item
		}
	}, target_doc, set_missing_values)
	return doc