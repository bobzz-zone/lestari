# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	add_months,
	cint,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
	now
)

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
		doc.subcustomer = self.subcustomer
		doc.warehouse = inv.warehouse
		doc.posting_date = now()
		doc.tutupan = self.tutupan
		# doc.janji_bayar = self.name
		doc.sales_bundle = self.sales_bundle
		doc.total_invoice = inv.outstanding
		baris_baru = {
			'gold_invoice':inv.name,
			'total':inv.outstanding,
			'due_date':inv.due_date,
			'total':inv.grand_total
		}
		doc.append("invoice_table",baris_baru)
		baris_baru1 = {
				'janji_bayar':self.name,
				'no_invoice':self.gold_invoice,
				'customer':self.customer,
				'tanggal_janji':self.tanggal_janji,
				'total_janji_bayar':self.total_bayar,
				'idr_janji_terbayar':self.total_terbayar,
				'sisa_janji':self.sisa_janji,
				'status_janji':self.status
			}
		doc.append("list_janji_bayar",baris_baru1)
		baris_baru2 = {
			'mode_of_payment': "Kas Sales",
			'amount': self.sisa_janji
		}
		doc.append("idr_payment",baris_baru2)
		total_idr_payment = 0
		total_idr_gold = 0
		total_payment = 0
		unallocated_payment = 0
		total_idr_payment += self.sisa_janji
		total_idr_gold += flt(total_idr_payment) / flt(self.tutupan)
		total_payment += flt(total_idr_payment) / flt(self.tutupan)
		unallocated_payment += flt(total_idr_payment) / flt(self.tutupan)
		doc.total_idr_payment = total_idr_payment
		doc.total_idr_gold = total_idr_gold
		doc.total_payment = total_payment
		doc.unallocated_payment = unallocated_payment
		doc.flags.ignore_permissions = True
		doc.save()
		return doc
	@frappe.whitelist(allow_guest=True)
	def get_deposit(self):
		doc = frappe.new_doc("Customer Deposit")
		doc.customer = self.customer
		doc.subcustomer = self.subcustomer
		doc.posting_date = now()
		doc.janji_bayar = self.name
		doc.sisa_janji=self.sisa_janji
		baris_baru = {
			'janji_bayar' : self.name,
			'no_invoice' : self.gold_invoice,
			'customer' : self.customer,
			'tanggal_janji' : self.tanggal_janji,
			'total_janji_bayar' : self.total_bayar,
			'idr_janji_bayar' : self.total_idr_payment,
			'sisa_janji' : self.sisa_janji,
			'status_janji' : self.status
		}
		doc.append('list_janji_bayar', baris_baru)
		doc.deposit_type = "IDR"
		doc.sales_bundle = self.sales_bundle
		doc.flags.ignore_permissions = True
		doc.save()
		return doc
