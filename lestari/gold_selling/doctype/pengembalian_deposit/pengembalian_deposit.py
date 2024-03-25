# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

class PengembalianDeposit(Document):
	pass
	def on_submit(self):
		self.make_gl_entries()
		frappe.db.sql("""update `tabCustomer Deposit` set idr_left=0,gold_left=0 where name="{}" """.format(self.deposit),as_list=1)
	def on_cancel(self):
		self.make_gl_entries()
		frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left+{},gold_left=gold_left+{} where name="{}" """.format(self.amount,self.gold_amount,self.deposit),as_list=1)
	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries

		if not gl_entries:
			gl_entries = self.get_gl_entries()

		#frappe.msgprint(gl_entries)
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
				piutang_gold = self.gold_account
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
		
		gl_entries = []
		gl = {}
		
		gl_piutang = []
		fiscal_years = get_fiscal_years(self.date, company=self.company)[0][0]
		deposit=frappe.get_doc("Customer Deposit",self.deposit)
		#1 untuk GL untuk piutang Gold
		piutang_gold = self.gold_account
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		#piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		nilai_kembali=0
		nilai_selisih_kurs = 0
		gold_amount = 0
		against=self.idr_account
		payment_account=get_bank_cash_account(self.mode_of_payment,self.company)["account"]
		#hitung selisih kurs untuk DP
		#positif kalo tutupan saat ini lebih besar... dan lebih besar adalah rugi kurs
		if self.deposit_type=="Emas":
			nilai_selisih_kurs=gold_amount*(self.tutupan-self.old_tutupan)
		
			#perlu check selisih kurs dari tutupan
			#lebih dr 0 itu debit
			if nilai_selisih_kurs>0:
				gl[selisih_kurs]=self.gl_dict(cost_center,selisih_kurs,nilai_selisih_kurs,0,fiscal_years,payment_account)
			else:
				gl[selisih_kurs]=self.gl_dict(cost_center,selisih_kurs,0,nilai_selisih_kurs,fiscal_years,payment_account)
			nilai_kembali = gold_amount*self.tutupan
			against=self.gold_account
			gl_piutang.append({
					"posting_date":self.date,
					"account":self.gold_account,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":nilai_kembali,
					"credit":0,
					"account_currency":"GOLD",
					"debit_in_account_currency":self.gold_amount,
					"credit_in_account_currency":0,
					"against":payment_account,
					"voucher_type":"Pengembalian Deposit",
					"voucher_no":self.name,
					#"remarks":"",
					"is_opening":"No",
					"is_advance":"No",
					"fiscal_year":fiscal_years,
					"company":self.company,
					"is_cancelled":0
				})
			frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Payment",against_voucher="{}" where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,self.deposit,self.gold_account),as_list=1)
		else:
			nilai_kembali=amount
			gl_piutang.append({
					"posting_date":self.date,
					"account":self.idr_account,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":nilai_kembali,
					"credit":0,
					"account_currency":"IDR",
					"against":payment_account,
					"debit_in_account_currency":nilai_kembali,
					"credit_in_account_currency":0,
					"voucher_type":"Pengembalian Deposit",
					"voucher_no":self.name,
					"is_opening":"No",
					"is_advance":"No",
					"fiscal_year":fiscal_years,
					"company":self.company,
					"is_cancelled":0
				})
			frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Payment",against_voucher="{}" where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,self.deposit,self.idr_account),as_list=1)
		gl[payment_account]=self.gl_dict(cost_center,payment_account,0,nilai_kembali,fiscal_years,against)
		
		
		for row in gl_piutang:
			gl_entries.append(frappe._dict(row))

		for row in gl:
			gl_entries.append(frappe._dict(gl[row]))

		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries
	@frappe.whitelist()
	def gl_dict(self,cost_center,account,debit,credit,fiscal_years,against):
		return {
					"posting_date":self.date,
					"account":account,
					"party_type":"",
					"party":"",
					"cost_center":cost_center,
					"debit":debit,
					"credit":credit,
					"account_currency":"IDR",
					"debit_in_account_currency":debit,
					"credit_in_account_currency":credit,
					"against":against,
					"voucher_type":"Pengembalian Deposit",
					"voucher_no":self.name,
					"is_opening":"No",
					"is_advance":"No",
					"fiscal_year":fiscal_years,
					"company":self.company,
					"is_cancelled":0
				}