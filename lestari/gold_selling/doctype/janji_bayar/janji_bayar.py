# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class JanjiBayar(Document):
	def validate(self):
		self.status = "Pending"
		self.sisa_janji=self.total_bayar
	def on_cancel(self):
		self.status="Cancelled"
	@frappe.whitelist(allow_guest=True)
	def get_gold_payment(self):
		inv = frappe.get_doc("Gold Invoice",self.gold_invoice)
		doc = frappe.new_doc("Gold Payment")
		doc.customer = self.customer
		doc.warehouse = inv.warehouse
		doc.posting_date = now()
		doc.janji_bayar = self.name
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
	@frappe.whitelist(allow_guest=True)
	def get_deposit(self):
		doc = frappe.new_doc("Customer Deposit")
		doc.customer = self.customer
		doc.posting_date = now()
		doc.janji_bayar = self.name
		doc.sisa_janji=self.sisa_janji
		doc.deposit_type = "IDR"
		
		doc.flags.ignore_permissions = True
		doc.save()
		return doc
