# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ReparasiInvoice(Document):
	@frappe.whitelist()
	def get_order(self):
		doc = frappe.get_doc("Reparasi Order",self.reparasi_order)
		for row in doc.items:
			baris_baru = {
				"item": row.item,
				"qty": row.qty,
				"bruto": row.bruto
			}
			self.append("items",baris_baru)


	def on_submit(self):
		sinv = frappe.new_doc("Sales Invoice")
		sinv.customer = self.customer
		sinv.debit_to = "110.402.000 - Piutang Reparasi - LMS"
		for row in self.harga_reparasi:
			baris_baru = {
				"item_code": row.jenis_jasa,
				"rate":row.rate,
				"qty":row.bruto,
				"income_account":"430.100.000 - Pendapatan Jasa Reparasi - LMS"
			}
			sinv.append("items",baris_baru)
		sinv.flags.ignore_permissions = True
		sinv.save()
