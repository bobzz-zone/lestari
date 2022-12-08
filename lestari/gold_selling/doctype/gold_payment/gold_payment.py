# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.controllers.stock_controller import StockController
class GoldPayment(StockController):
	def validate(self):
		#seharusnya validasi agaryang belum due, di pastikan tutupan sama..atau hanya 1 invoice agar di gold payment tutupan di samakan
		#check unallocated harus 0
		unallocated=self.total_payment
		for row in self.invoice_table:
			if row.allocated:
				unallocated=unallocated-row.allocated
		for row in self.customer_return:
			if row.allocated:
				unallocated=unallocated-row.allocated
		self.unallocated=unallocated
		if self.unallocated_payment and self.unallocated_payment>0.0001:
			frappe.throw("Error,unallocated Payment Masih tersisa {}".format(self.unallocated_payment))
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
	def on_submit(self):
		self.make_gl_entries()
		#posting Stock Ledger Post
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		#update invoice
		for row in self.invoice_table:
			if row.allocated==row.outstanding:
				frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding-{} , invoice_status="Paid" where name = "{}" """.format(row.allocated,row.gold_invoice))
			else:
				frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding-{} where name = "{}" """.format(row.allocated,row.gold_invoice))
		for row in self.customer_return:
			if row.allocated==row.outstanding:
				frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} , invoice_status="Paid" where name = "{}" """.format(row.allocated,row.invoice))
			else:
				frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} where name = "{}" """.format(row.allocated,row.invoice))
	def on_cancel(self):
		self.flags.ignore_links=True
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		#update invoice
		for row in self.invoice_table:
			frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.allocated,row.gold_invoice))
		for row in self.customer_return:
			frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.allocated,row.invoice))

	@frappe.whitelist()
	def get_gold_invoice(self):
		doc = frappe.db.get_list("Gold Invoice", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','outstanding','due_date','tutupan','total_bruto','grand_total'])
		for row in doc:
			# frappe.msgprint(str(row))
			self.total_invoice = self.total_invoice + row.outstanding
			baris_baru = {
				'gold_invoice':row.name,
				'outstanding':row.outstanding,
				'total':row.grand_total,
				'due_date':row.due_date,
				'total_bruto':row.total_bruto,
				'tutupan':row.tutupan
			}
			self.append("invoice_table",baris_baru)
		doc = frappe.db.get_list("Customer Payment Return", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','outstanding','due_date','tutupan','total'])
		for row in doc:
			# frappe.msgprint(str(row))
			self.total_invoice = self.total_invoice + row.outstanding
			baris_baru = {
				'invoice':row.name,
				'total':row.total,
				'outstanding':row.outstanding,
				'due_date':row.due_date,
				'tutupan':row.tutupan
			}
			self.append("customer_return",baris_baru)

	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		for row in self.stock_payment:
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
				"dependant_sle_voucher_detail_no": row.name,
				"is_cancelled":1 if self.docstatus == 2 else 0
				})
		for row in sl:
			sl_entries.append(frappe._dict(row))

		# reverse sl entries if cancel
		# if self.docstatus == 2:
		# 	sl_entries.reverse()

		self.make_sl_entries(sl_entries)
	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()
		print(gl_entries)
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
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		gl_entries=[]
		gl={}
		gl_piutang=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')

		#mapping allocated
		inv_payment_map={}
		for row in self.invoice_table:
			inv_payment_map[row.gold_invoice]=row.allocated
		for row in self.customer_return:
			inv_payment_map[row.invoice]=row.allocated
		nilai_selisih_kurs=0
		# distribute total gold perlu bagi per invoice
		sisa= self.total_payment
		for row in self.invoice_table:
			if sisa>0 and row.allocated>0:
				payment=row.allocated
				if sisa<row.allocated:
					payment=sisa;
				inv_payment_map[row.gold_invoice]=inv_payment_map[row.gold_invoice]-payment
				gl_piutang.append({
								"posting_date":self.posting_date,
								"account":piutang_gold,
								"party_type":"Customer",
								"party":self.customer,
								"cost_center":cost_center,
								"debit":0,
								"credit":payment*row.tutupan,
								"account_currency":"GOLD",
								"debit_in_account_currency":0,
								"credit_in_account_currency":payment,
								#"against":"4110.000 - Penjualan - L",
								"voucher_type":"Gold Payment",
								"against_voucher_type":"Gold Invoice",
								"against_voucher":row.gold_invoice,
								"voucher_no":self.name,
								#"remarks":"",
								"is_opening":"No",
								"is_advance":"No",
								"fiscal_year":fiscal_years,
								"company":self.company,
								"is_cancelled":0
								})
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*payment)
		for row in self.customer_return:
			if sisa>0 and row.allocated>0:
				payment=row.allocated
				if sisa<row.allocated:
					payment=sisa;
				inv_payment_map[row.invoice]=inv_payment_map[row.invoice]-payment
				gl_piutang.append({
								"posting_date":self.posting_date,
								"account":piutang_gold,
								"party_type":"Customer",
								"party":self.customer,
								"cost_center":cost_center,
								"debit":0,
								"credit":payment*row.tutupan,
								"account_currency":"GOLD",
								"debit_in_account_currency":0,
								"credit_in_account_currency":payment,
								#"against":"4110.000 - Penjualan - L",
								"voucher_type":"Gold Payment",
								"against_voucher_type":"Customer Payment Return",
								"against_voucher":row.invoice,
								"voucher_no":self.name,
								#"remarks":"",
								"is_opening":"No",
								"is_advance":"No",
								"fiscal_year":fiscal_years,
								"company":self.company,
								"is_cancelled":0
								})
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*payment)
		for row in gl_piutang:
			gl_entries.append(frappe._dict(row))
		#perlu check selisih kurs dari tutupan
		#lebih dr 0 itu debit
		dsk=0
		csk=0
		if nilai_selisih_kurs!=0:
			if nilai_selisih_kurs<0:
				dsk=nilai_selisih_kurs
			else:
				csk=nilai_selisih_kurs
			gl[selisih_kurs]={
									"posting_date":self.posting_date,
									"account":selisih_kurs,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":dsk,
									"credit":csk,
									"account_currency":"IDR",
									"debit_in_account_currency":dsk,
									"credit_in_account_currency":csk,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Payment",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		#BONUS,DISCOUNT,WRITEOFF
		if self.bonus>0:
			bonus_payment = frappe.db.get_single_value('Gold Selling Settings', 'bonus_payment')
			gl[bonus_payment]={
									"posting_date":self.posting_date,
									"account":bonus_payment,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":self.bonus*self.tutupan,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.bonus*self.tutupan,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Payment",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		if self.discount_amount>0:
			discount_payment = frappe.db.get_single_value('Gold Selling Settings', 'discount_payment')
			gl[discount_payment]={
									"posting_date":self.posting_date,
									"account":discount_payment,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":self.discount_amount*self.tutupan,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.discount_amount*self.tutupan,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Payment",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		if self.write_off>0:
			gl[self.write_off_account]={
									"posting_date":self.posting_date,
									"account":self.write_off_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":self.write_off*self.tutupan,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.write_off*self.tutupan,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Payment",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if self.total_gold_payment>0:
			warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
			gl[warehouse_account]={
									"posting_date":self.posting_date,
									"account":warehouse_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":self.total_gold_payment*self.tutupan,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.total_gold_payment*self.tutupan,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Payment",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		
		#untuk payment IDR
		if self.total_idr_payment>0:
			#journal IDR nya aja
			for row in self.idr_payment:
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
										"voucher_type":"Gold Payment",
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
#		frappe.msgprint(gl_entries)
		return gl_entries
