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
		target.nthko_id = source.get("nthko_id")
		target.s_warehouse = source_parent.get("s_warehouse")
		target.t_warehouse = source.get("t_warehouse")
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