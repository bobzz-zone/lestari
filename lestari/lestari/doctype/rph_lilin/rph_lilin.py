# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today
from six import string_types

class RPHLilin(Document):
	def on_submit(self):
		sumber_doc = self
		for row in sumber_doc.tabel_detail:
			for col in range(row.jumlah_pohon):
				# target_doc.proses = sumber_doc.proses
				# sumber_resep = frappe.db.get_list("Resep Mul Karet", filters={"final_product":row.produk})		
				sumber_resep = frappe.db.sql("""
				SELECT
				rubber_mould,
				hasil_inject,
				final_product,
				name
				FROM `tabResep Mul Karet`
				WHERE final_product = "{}"
				""".format(row.produk_id),as_dict=1)
				frappe.msgprint(str(sumber_resep))
				for col in sumber_resep:
					# frappe.msgprint(col)
					if row.qty_isi_pohon:
						baris_baru={
							"no_spk":row.no_spk,
							"produk_id":row.produk_id,
							"mul_karet":col.rubber_mould,
							"resep_mul_karet":col.name,
							"qty":row.qty_isi_pohon,
							"inject":col.hasil_inject,
							"logo":frappe.get_doc("Item",row.produk_id).brand
							}
					target_doc = frappe.new_doc("Data Pohon Lilin")
					target_doc.append("resep",baris_baru)
					target_doc.warehouse = "Lilin - LMS"
					target_doc.kadar = row.kadar
					target_doc.flags.ignore_permissions = True
					target_doc.save()
					target_doc.submit()

@frappe.whitelist()
def get_items_from_spk_produksi(source_name, target_doc=None, args=None):
	# requested_item_qty = get_requested_item_qty(source_name)

	if args is None:
		args = {}
	if isinstance(args, string_types):
		args = json.loads(args)

	def update_item(source, target, source_parent):
		target.qty = source.get("qty")
		target.produk_id = source.get("produk_id")
		target.no_spk = source_parent.get("name")
		target.kadar = source.get("kadar")
		target.customer = source.get("customer")
		target.qty_isi_pohon = source.get("qty_isi_pohon")
		target.kategori = source.get("kategori")
		target.sub_kategori = source.get("sub_kategori")
		target.jumlah_pohon = source.get("jumlah_pohon")
		target.target_berat = source.get("target_berat")

	def select_item(d):
		filtered_items = args.get('filtered_children', [])
		child_filter = d.name in filtered_items if filtered_items else True

		return child_filter

	doc = get_mapped_doc("SPK Produksi", source_name, {
		"SPK Produksi": {
			"doctype": "RPH Lilin",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"SPK Produksi Detail": {
			"doctype": "RPH Lilin Detail",
			"field_map": 
			[
				["name", "spk_produksi_detail"],
				["parent", "spk_produksi"]
			],
			"postprocess": update_item,
			"condition": select_item
		}
	}, target_doc)

	return doc