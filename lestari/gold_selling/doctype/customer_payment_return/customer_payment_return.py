# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.stock_ledger import NegativeStockError, get_previous_sle, get_valuation_rate
class CustomerPaymentReturn(StockController):
	def validate(self):
		#seharusnya validasi agaryang belum due, di pastikan tutupan sama..atau hanya 1 invoice agar di gold payment tutupan di samakan
		#check unallocated harus 0
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
		if self.total<=1:
			frappe.throw("Error Tidak ada nilai yang dikembalikan")
	def on_submit(self):
		for row in self.items:
			row.valuation_rate = get_valuation_rate(
					row.item,
					self.warehouse,
					self.doctype,
					self.name,
					0,
					currency=erpnext.get_company_currency(self.company),
					company=self.company,
					raise_error_if_no_rate=True
				)
			if not row.valuation_rate or row.valuation_rate==0:
				frappe.throw("Error Barang Tidak ada Nilai")
			row.total_amount=row.qty*row.valuation_rate
		self.make_gl_entries()
		#posting Stock Ledger Post
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		
	def on_cancel(self):
		self.flags.ignore_links=True
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		#perlu check hpp outnya
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		for row in self.items:
			sl.append({
				"item_code":row.item,
				"actual_qty":row.qty*-1,
				"fiscal_year":fiscal_years,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": self.company,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"is_cancelled": 0,
				"stock_uom":frappe.db.get_value("Item", row.item, "stock_uom"),
				"warehouse":self.warehouse,
				"valuation_rate":row.valuation_rate,
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
		gl_entries=[]
		gl={}
		gl_piutang=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if self.total>0:
			#hpp perlu di update dulu
			warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
			total_value=0
			for row in self.items:
				total_value=total_value+row.total_amount
			gl[warehouse_account]={
									"posting_date":self.posting_date,
									"account":warehouse_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"credit":total_value,
									"debit":0,
									"account_currency":"IDR",
									"credit_in_account_currency":total_value,
									"debit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Payment Return",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
			gl[piutang_gold]={
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":total_value,
									"credit":0,
									"account_currency":"GOLD",
									"debit_in_account_currency":self.total,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Payment Return",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		
			for row in gl:
				gl_entries.append(frappe._dict(gl[row]))
			gl_entries = merge_similar_entries(gl_entries)
			return gl_entries