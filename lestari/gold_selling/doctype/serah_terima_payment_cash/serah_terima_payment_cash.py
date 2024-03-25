# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime ,now
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from frappe.utils import flt

class SerahTerimaPaymentCash(Document):
	@frappe.whitelist()
	def get_payment(self):
		self.payment = {}
		payment = frappe.get_list('IDR Payment',
					filters={'docstatus': 1,'mode_of_payment':["in",['Cash','Kas Sales']],'is_done':["<",1],"creation":[">=","2024/01/01"]}, 
					fields=['parent','parenttype','name','mode_of_payment','amount','is_done'])
		total_cash = 0
		for row in payment:
			# frappe.msgprint(row)
			bundle = frappe.get_value(row.parenttype, row.parent, 'sales_bundle')
			sales = frappe.get_value("Sales Stock Bundle", bundle, 'sales')
			if self.sales:
				if self.sales == sales:
					if self.bundle:
						if self.bundle == bundle:
							total_cash += row.amount
							payment_baru = {
								'mode_of_payment': row.mode_of_payment,
								'bundle': bundle,
								'sales': sales,
								'amount': row.amount,
								'customer': frappe.get_value(row.parenttype, row.parent, 'customer'),
								'deposit_account': frappe.get_doc('Mode of Payment', row.mode_of_payment).accounts[0].default_account,
								'voucher_type':row.parenttype,
								'voucher_no':row.parent,
								'child_table':"IDR Payment",
								'child_id':row.name
							}
							self.append('payment',payment_baru)
					else:
						total_cash += row.amount
						payment_baru = {
							'mode_of_payment': row.mode_of_payment,
							'bundle': bundle,
							'sales': sales,
							'amount': row.amount,
							'customer': frappe.get_value(row.parenttype, row.parent, 'customer'),
							'deposit_account': frappe.get_doc('Mode of Payment', row.mode_of_payment).accounts[0].default_account,
							'voucher_type':row.parenttype,
							'voucher_no':row.parent,
							'child_table':"IDR Payment",
							'child_id':row.name
						}
						self.append('payment',payment_baru)
			else:
				total_cash += row.amount
				payment_baru = {
					'mode_of_payment': row.mode_of_payment,
					'bundle': bundle,
					'sales': sales,
					'amount': row.amount,
					'customer': frappe.get_value(row.parenttype, row.parent, 'customer'),
					'deposit_account': frappe.get_doc('Mode of Payment', row.mode_of_payment).accounts[0].default_account,
					'voucher_type':row.parenttype,
					'voucher_no':row.parent,
					'child_table':"IDR Payment",
					'child_id':row.name
				}
				self.append('payment',payment_baru)
			# baris_baru = {
			# 	'amount':row.amount,
			# 	'voucher_type':row.parenttype,
			# 	'voucher_no':row.parent,
			# 	'child_table':"Stock Payment",
			# 	'child_id':row.name
			# }
			# frappe.msgprint(baris_baru)
			# self.append('details',baris_baru)
		self.nilai_cash = total_cash
	def on_submit(self):
		# self.make_gl_entries()
		je = frappe.new_doc('Journal Entry')
		je.voucher_type = "Journal Entry"
		account_kas = frappe.db.get_single_value('Gold Selling Settings','default_kas_kantor')
		je.append('accounts',{'account':account_kas,"debit_in_account_currency":self.nilai_cash})
		for row in self.payment:
			baris_baru = {
				'account' : row.deposit_account,
				'credit_in_account_currency' : row.amount,
				'user_remark' : self.name
			}
			je.append('accounts', baris_baru)
			frappe.db.set_value("IDR Payment", row.child_id, "is_done", 1)
		je.posting_date = self.posting_date
		je.bill_no = self.name
		je.bill_date = self.posting_date
		je.flags.ignore_permissions = True
		je.save()
		je.submit()
		self.voucher_no = je.name
		self.save()

	def on_cancel(self):
		doc = frappe.get_doc("Journal Entry", self.voucher_no)
		doc.cancel()
		# self.make_gl_entries()
		for row in self.payment:
			frappe.db.set_value("IDR Payment", row.child_id, "is_done", 0)

	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		account_kas = frappe.db.get_single_value('Gold Selling Settings','default_kas_kantor')
		gl={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		cost_center = frappe.db.get_single_value('Gold Selling Settings','cost_center')
		company = "Lestari Mulia Sentosa"
		#add GL untuk kas besar
		gl[account_kas]={
			"posting_date":self.posting_date,
			"account":account_kas,
			"party_type":"",
			"party":"",
			"cost_center":cost_center,
			"debit":self.nilai_cash,
			"credit":0,
			"account_currency":"IDR",
			"debit_in_account_currency":self.nilai_cash,
			"credit_in_account_currency":0,
			"voucher_type":"Gold Invoice",
			"voucher_no":self.name,
			"is_opening":"No",
			"is_advance":"No",
			"fiscal_year":fiscal_years,
			"company":company,
			"is_cancelled":0
		}	
		for row in self.payment:
			gl[row.deposit_account]={
				"posting_date":self.posting_date,
				"account":row.deposit_account,
				"party_type":"",
				"party":"",
				"cost_center":cost_center,
				"debit":0,
				"credit":row.amount,
				"account_currency":"IDR",
				"debit_in_account_currency":0,
				"credit_in_account_currency":row.amount,
				#"against":"4110.000 - Penjualan - L",
				"voucher_type": row.voucher_type,
				"voucher_no": row.voucher_no,
				#"remarks":"",
				"is_opening":"No",
				"is_advance":"No",
				"fiscal_year":fiscal_years,
				"company":company,
				"is_cancelled":0
			}
		gl_entries=[]
		for row in gl:
			if 'remarks' in gl[row]:
				pass
			else:
				gl[row]['remarks']=""
			gl_entries.append(frappe._dict(gl[row]))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries

	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()
		if gl_entries:
			update_outstanding = "Yes"

			if self.docstatus == 1:
				make_gl_entries(
					gl_entries,
					update_outstanding=update_outstanding,
					merge_entries=False,
					from_repost=from_repost,
				)
			elif self.docstatus == 2:
				make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

			if update_outstanding == "No":
				from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
				# piutang_gold = self.piutang_gold
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 :
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)