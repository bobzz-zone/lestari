# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today
from six import string_types

class SPKOInjectLilin(Document):
	pass

@frappe.whitelist()
def get_items_from_rph_lilin(source_name, target_doc=None, args=None):

	if args is None:
		args = {}
	if isinstance(args, string_types):
		args = json.loads(args)

	def update_item(source, target, source_parent):
		target.spk_ppic = source.get("no_spk")
		target.item = source.get("produk_id")
		target.qty = source.get("qty")
		target.kadar = source.get("kadar")
		# target.inject = frappe.db.get_value('SPK Lilin Item',{'no_spk':source.get("no_spk"),'produk':source.get("produk_id")},'inject')
		# target.rekap_lilin = frappe.db.get_value('SPK Lilin Item',{'no_spk':source.get("no_spk"),'produk':source.get("produk_id")},'parent')
		# target.stone_note = frappe.db.get_value('SPK Lilin Item',{'no_spk':source.get("no_spk"),'produk':source.get("produk_id")},'keterangan_batu')
		# target.resep = frappe.db.get_value('SPK Lilin Item',{'no_spk':source.get("no_spk"),'produk':source.get("produk_id")},'resep_mul_karet')

	def select_item(d):
		filtered_items = args.get('filtered_children', [])
		child_filter = d.name in filtered_items if filtered_items else True

		return child_filter

	doc = get_mapped_doc("RPH Lilin", source_name, {
		"RPH Lilin": {
			"doctype": "SPKO Inject Lilin",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"RPH Lilin Detail": {
			"doctype": "SPKO Inject Lilin Item",
			"field_map": {
				"name": "rph_lilin_detail",
				"parent": "rph_lilin"
			},"postprocess": update_item,
			"condition": select_item
		}
	}, target_doc)
	# frappe.msgprint(str(doc))
	return doc
