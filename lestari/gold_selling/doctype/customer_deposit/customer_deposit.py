# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
class CustomerDeposit(Document):
	def validate(self):
		#total items
		if self.is_convert==1:
			self.stock_deposit=[]
			if self.customer_deposit_source and self.sisa_idr_deposit>0:
				item_ct = frappe.db.get_single_value('Gold Selling Settings', 'item_ct')
				qty = self.sisa_idr_deposit/self.tutupan
				self.append("stock_deposit",{"item":item_ct,"rate":100,"qty":qty,"amount":qty})
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
	def on_submit(self):
		self.make_gl_entries()
	def on_cancel(self):
		self.make_gl_entries()

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
				piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 :
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		if self.total_gold_deposit>0:
			piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
			warehouse_account = get_warehouse_account_map(self.company)
			gl[piutang_gold]={
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":0,
									"credit":self.total_gold_deposit*self.tutupan,
									"account_currency":"GOLD",
									"debit_in_account_currency":0,
									"credit_in_account_currency":self.total_gold_deposit,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"Yes",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
			gl[warehouse_account]={
									"posting_date":self.posting_date,
									"account":warehouse_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":self.total_gold_deposit*self.tutupan,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.total_gold_deposit*self.tutupan,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		#untuk deposit IDR
		if self.total_idr_deposit>0:
			piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
			gl[piutang_idr]={
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":0,
									"credit":self.total_idr_deposit,
									"account_currency":"IDR",
									"debit_in_account_currency":0,
									"credit_in_account_currency":self.total_idr_deposit,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"Yes",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
			for row in self.idr_deposit:
				account=get_bank_cash_account(row.mode_of_payment,self.company)
				if account in gl:
					gl[account]['debit']=gl[account]['debit']+row.amount
					gl[account]['debit_in_account_currency']=gl[account]['debit']
				else:
					gl[account]={
										"posting_date":self.posting_date,
										"account":account,
										"party_type":"",
										"party":"",
										"cost_center":cost_center,
										"debit":row.amount,
										"credit":0,
										"account_currency":"IDR",
										"debit_in_account_currency":row.amount,
										"credit_in_account_currency":0,
										#"against":"4110.000 - Penjualan - L",
										"voucher_type":"Gold Invoice",
										"voucher_no":self.name,
										#"remarks":"",
										"is_opening":"No",
										"is_advance":"No",
										"fiscal_year":fiscal_years,
										"company":self.company,
										"is_cancelled":0
										}
		
		gl_entries=[]
		for row in gl:
			gl_entries.append(frappe._dict(gl[row]))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries