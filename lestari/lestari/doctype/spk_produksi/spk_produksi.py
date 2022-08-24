# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today

class SPKProduksi(Document):
	pass

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):

	def update_item(source, target, source_parent):
		target.qty = source.get("qty")
		target.produk_id = source.get("item_code")
		target.no_spk = source_name
		target.jumlah_pohon = source.jumlah_pohon
		target.qty_isi_pohon = source.qty_isi_pohon
		target.target_berat = source.target_berat
		sub_kategori = frappe.get_doc("Item",source.get("item_code")).item_group
		target.kategori = frappe.get_doc("Item Group",sub_kategori).parent_item_group
		target.sub_kategori = sub_kategori
		target.kadar = frappe.get_doc("Item",source.get("item_code")).kadar
		target.customer = source_parent.customer
		target.so_type = source_parent.order_type

	doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "SPK Produksi",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Order Item": {
			"doctype": "SPK Produksi Detail",
			"field_map": {
				"name": "sales_order_item",
				"parent": "sales_order"
			},"postprocess": update_item
		}
	}, target_doc)

	return doc

# @frappe.whitelist()
# def get_material_request(source_name, target_doc=None):

# 	def update_item(source, target, source_parent):	
# 		target.qty = source.get("qty")
# 		target.produk_id = source.get("item_code")
# 		target.no_spk = source_name
# 		target.kadar = frappe.get_doc("Item",source.get("item_code")).kadar
# 		target.customer = source_parent.customer
# 		target.so_type = source_parent.order_type

# 	doc = get_mapped_doc("Material Request", source_name, {
# 		"Material Request": {
# 			"doctype": "SPK Produksi",
# 			"validation": {
# 				"docstatus": ["=", 1]
# 			}
# 		},
# 		"Material Request Item": {
# 			"doctype": "SPK Produksi Detail",
# 			"field_map": {
# 				"name": "material_request_item",
# 				"parent": "material_request"
# 			},"postprocess": update_item
# 		}
# 	}, target_doc)

# 	return doc
