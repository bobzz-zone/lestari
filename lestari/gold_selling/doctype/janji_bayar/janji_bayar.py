# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class JanjiBayar(Document):
	def on_submit(self):
		self.sisa_janji=self.total_bayar
	@frappe.whitelist(allow_guest=True)
	def get_gold_payment(self):
		inv = frappe.get_doc("Gold Invoice",self.gold_invoice)
		doc = frappe.new_doc("Gold Payment")
		doc.customer = self.customer
		doc.warehouse = inv.warehouse
		doc.posting_date = now()
		doc.janji_bayar=self.janji_bayar
		doc.total_invoice = inv.outstanding
		baris_baru = {
			'gold_invoice':inv.name,
			'total':inv.outstanding,
			'due_date':inv.due_date,
			'total':inv.grand_total
		}
		doc.append("invoice_table",baris_baru)

		doc.flags.ignore_permissions = True
		doc.save()
		return doc
