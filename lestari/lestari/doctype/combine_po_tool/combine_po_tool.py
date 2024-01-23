# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CombinePOTool(Document):
	@frappe.whitelist()
	def buat_po(self):
		pr_list = frappe.db.get_list("Purchase Order", fields={'transaction_date':self.posting_date, 'docstatus':0, 'supplier':self.supplier})
		frappe.msgprint(str(pr_list))
		new_doc = frappe.new_doc("Purchase Order")
		new_doc.supplier = self.supplier
		new_doc.transaction_date = self.posting_date
		new_doc.naming_series = "PO.YY.MM.DD.###"
		for row in pr_list:
			po = frappe.get_doc("Purchase Order", row.name)
			for col in po.items:
				baris_baru = {
					"item_code": col.item_code,
					"schedule_date": col.schedule_date,
					"description": col.description,
					"qty": col.qty,
					"uom": col.uom,
					"stock_uom": col.stock_uom,
					"conversion_factor": col.conversion_factor,
					"rate": col.rate,
					"amount": col.amount,
					"base_rate": col.base_rate,
					"base_amount": col.base_amount,
					"material_request": col.material_request,
					"material_request_item": col.material_request_item
				}
				frappe.msgprint(str(baris_baru))
				new_doc.append("items",baris_baru)
		new_doc.flags.ignore_permissions = True
		new_doc.ignore_if_duplicate = False
		new_doc.save()
		# frappe.msgprint(new_doc.name)
		for row in pr_list:
			frappe.delete_doc('Purchase Order', row.name)
