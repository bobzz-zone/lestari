# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today
from six import string_types

class RPHBSP(Document):
	pass

@frappe.whitelist()
def get_items_from_transfer_material(source_name, target_doc=None, args=None):
	# requested_item_qty = get_requested_item_qty(source_name)

	if args is None:
		args = {}
	if isinstance(args, string_types):
		args = json.loads(args)

	def update_item(source, target, source_parent):
		target.no_spk = source.get("nthko_id")
		target.operation = source.get("bsp_operation")
		material = frappe.get_doc(source.get("nthko_area"),source.get("nthko_id"))
		for row in material.table_detail:
			target.produk_id = row.produk_id
			target.kadar = frappe.get_doc('Item',row.produk_id).kadar
			target.sub_kategori = frappe.get_doc('Item',row.produk_id).item_group
			target.kategori = frappe.get_doc('Item Group',frappe.get_doc('Item',row.produk_id).item_group).parent_item_group
			# target.qty = row.

	def select_item(d):
		filtered_items = args.get('filtered_children', [])
		child_filter = d.name in filtered_items if filtered_items else True

		return child_filter

	doc = get_mapped_doc("Transfer Material", source_name, {
		"Transfer Material": {
			"doctype": "RPH BSP",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Transfer Material Detail": {
			"doctype": "RPH BSP Detail",
			"field_map": 
			[
				["name", "transfer_material_detail"],
				["parent", "transfer_material"]
			],
			"postprocess": update_item,
			"condition": select_item
		}
	}, target_doc)

	return doc