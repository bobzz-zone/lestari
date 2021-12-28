# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WorkOrderPohonan(Document):
	def validate():
		pass

@frappe.whitelist()
def make_stock_entry(no_dpl,no_wop):
	target_doc = frappe.new_doc("Stock Entry")
	target_doc.stock_entry_type = "Material Transfer"
	sumber_sprue = frappe.db.sql("""
		SELECT
		wop.main_sprue,
		item.item_code,
		item.stock_uom AS uom,
		itemdef.default_warehouse AS s_warehouse
		FROM `tabWork Order Pohonan` wop
		JOIN `tabData Pohon Lilin` dpl ON dpl.main_sprue = wop.main_sprue
		JOIN `tabData Set Sprue` dms ON dss.name = dpl.main_sprue
		JOIN `tabItem` item ON item.item_code = dss.name
		JOIN `tabItem Default` itemdef ON itemdef.parent = item.item_code
		WHERE ppl.name = "{}" AND dpl.name = "{}"
		""".format(no_wop, no_dpl), as_dict=1)

	for row in sumber_sprue:
		baris_baru = {
				"item_code": row.item_code,
				"qty": 1,
				"uom" : row.uom,
				"conversion_factor" : 1,
				"t_warehouse" : "Work In Progress - L",
				"s_warehouse" : row.s_warehouse
		}

	target_doc.append("items",baris_baru)
	target_doc.ignore_permissions = True
	target_doc.save()
	return target_doc.as_dict()