# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _, msgprint
from frappe.model.document import Document

class TransferMaterialTools(Document):

	def validate(self):
		data = self.get_material_recap()
		frappe.msgprint(str(data))

@frappe.whitelist()
def get_material_recap(item_group):
	data = frappe.db.sql("""
	SELECT 
	wo_it.item_code as item,
	wo_it.item_name, 
	wo_it.required_qty as qty,
	wo_it.parent as wo
	FROM `tabWork Order Item` wo_it
	LEFT JOIN `tabWork Order` wo 
	ON wo_it.parent = wo.name 
	LEFT JOIN `tabItem` it
	ON wo_it.item_name = it.name
	LEFT JOIN `tabItem Group` it_gr
	ON it.item_group = it_gr.name
	WHERE it_gr.name = "{}"
	""".format(item_group), as_dict=1)
	return data
		
# def get_wo_list():
# 	return frappe.db.get_list("Work Order",
# 		filters={
# 			'docstatus': '1'
# 			},
# 			fields=['name', 'production_item', 'item_name'],
# 			as_list=1
# 			)

# def get_wo_child_list():
# 	frappe.db.get_list("Work Order Item",
# 			filters={
# 				'docstatus': '1'
# 			},
# 			fields=['parent', 'item_code', 'item_name', 'required_qty'],
# 			as_list=1
# 			)

# @frappe.whitelist()
# def get_items_for_material_recap(doc, item_groups=None, get_parent_warehouse_data=None):
# 	if isinstance(doc, str):
# 		doc = frappe._dict(json.loads(doc))

# 	if item_groups:
# 		item_groups = list(set(get_item_groups_list(item_groups)))

# 		if doc.get("item_group") and not get_parent_warehouse_data and doc.get("item_group") in item_groups:
# 			item_groups.remove(doc.get("item_group"))

# 	doc['materials'] = []

# 	return mr_items

# def get_item_groups_list(item_groups):
# 	item_group_list = []

# 	if isinstance(item_groups, str):
# 		item_groups = json.loads(item_groups)

# 	for row in item_groups:
# 		child_item_groups = frappe.db.get_descendants('Item Group', row.get("item_group"))
# 		if child_item_groups:
# 			item_group_list.extend(child_item_groups)
# 		else:
# 			item_group_list.append(row.get("item_group"))

# 	return item_group_list	