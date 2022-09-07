# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.controllers.stock_controller import StockController
class CustomerDeposit(StockController):
	def validate(self):
		#total items
		if self.deposit_type=="Emas":
			if self.is_convert==0:
				self.idr_deposit=[]
		else:
			self.stock_deposit=[]
		if self.is_convert==1:
			self.stock_deposit=[]
			if self.customer_deposit_source and self.sisa_idr_deposit>0:
				item_ct = frappe.db.get_single_value('Gold Selling Settings', 'item_ct')
				qty = self.sisa_idr_deposit/self.tutupan
				self.append("stock_deposit",{"item":item_ct,"rate":100,"qty":qty,"amount":qty})
				self.total_gold_deposit=qty
				self.gold_left=qty
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
	def on_submit(self):
		self.make_gl_entries()
		#posting Stock Ledger Post
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		if self.is_convert==1:
			frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left-{} where name="{}" """.format(self.sisa_idr_deposit,self.customer_deposit_source),as_list=1)
	
	def on_cancel(self):
		self.flags.ignore_links=True
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		if self.is_convert==1:
			frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left+{} where name="{}" """.format(self.sisa_idr_deposit,self.customer_deposit_source),as_list=1)

	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		for row in self.stock_deposit:
			sl.append({
				"item_code":row.item,
				"actual_qty":row.qty,
				"fiscal_year":fiscal_years,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": self.company,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"is_cancelled": 0,
				"stock_uom":frappe.db.get_value("Item", row.item, "stock_uom"),
				"warehouse":self.warehouse,
				"incoming_rate":row.rate*self.tutupan/100,
				"recalculate_rate": 1,
				"dependant_sle_voucher_detail_no": row.name
				})
		for row in sl:
			sl_entries.append(frappe._dict(row))

		# reverse sl entries if cancel
		if self.docstatus == 2:
			sl_entries.reverse()

		self.make_sl_entries(sl_entries)
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
		if self.total_gold_deposit>0 and self.deposit_type=="Emas":
			piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
			warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
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
		#pelunasan kalo ada isconvert
			if self.is_convert==1:
				if self.customer_deposit_source and self.sisa_idr_deposit>0:
					piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
					gl[piutang_idr]={
									"posting_date":self.posting_date,
									"account":piutang_idr,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"credit":0,
									"debit":self.sisa_idr_deposit,
									"account_currency":"IDR",
									"credit_in_account_currency":0,
									"debit_in_account_currency":self.sisa_idr_deposit,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"against_voucher_type":"Customer Deposit",
									"voucher_no":self.name,
									"against_voucher":self.customer_deposit_source,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
					gl[self.cash_from]={
										"posting_date":self.posting_date,
										"account":self.cash_from,
										"party_type":"",
										"party":"",
										"cost_center":cost_center,
										"credit":self.sisa_idr_deposit,
										"debit":0,
										"account_currency":"IDR",
										"credit_in_account_currency":self.sisa_idr_deposit,
										"debit_in_account_currency":0,
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
		if self.total_idr_deposit>0 and self.deposit_type=="IDR":
			piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
			
			gl[piutang_idr]={
									"posting_date":self.posting_date,
									"account":piutang_idr,
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
				account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
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
										"voucher_type":"Customer Deposit",
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
@frappe.whitelist()
def get_idr_advance(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select name , idr_left from `tabCustomer Deposit` where name LIKE %(txt)s and deposit_type="IDR" and docstatus=1 and customer=%(customer)s """,
		{"customer": filters.get("customer", ""), "txt": "%" + txt + "%"},
	)
@frappe.whitelist()
def get_gold_advance(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select name , gold_left from `tabCustomer Deposit` where name LIKE %(txt)s and deposit_type="Emas" and docstatus=1 and customer=%(customer)s """,
		{"customer": filters.get("customer", ""), "txt": "%" + txt + "%"},
	)
