# Copyright (c) 2022, DAS and contributors
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
)
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.controllers.stock_controller import StockController

class GoldPayment(StockController):
	def validate(self):
		#seharusnya validasi agaryang belum due, di pastikan tutupan sama..atau hanya 1 invoice agar di gold payment tutupan di samakan
		#check unallocated harus 00
# <<<<<<< HEAD
# 		if self.unallocated_payment<0.0001:
# 			self.unallocated_payment = 0
# 		else:
# 			unallocated=self.total_payment
# 			for row in self.invoice_table:
# 				if row.allocated:
# 					# frappe.msgprint(row.allocated)
# 					unallocated=flt(unallocated,3)-flt(row.allocated,3)
# 			for row in self.customer_return:
# 				if row.allocated:
# 					unallocated=flt(unallocated,3)-flt(row.allocated,3)
# 			self.unallocated_payment=flt(unallocated,3)
# =======
		unallocated=self.total_payment+flt(self.total_advance)-flt(self.jadi_deposit)-flt(self.write_off)
		for row in self.invoice_table:
			if row.allocated:
				# frappe.msgprint(row.allocated)
				unallocated=flt(unallocated,3)-flt(row.allocated,3)
		for row in self.customer_return:
			if row.allocated:
				unallocated=flt(unallocated,3)-flt(row.allocated,3)
		unallocated=flt(unallocated,3)
		self.unallocated_payment=flt(unallocated,3)
# >>>>>>> 4ff73b59f620a2c5a1982c33c1414d63f5363615
		# if self.unallocated_payment and self.unallocated_payment>0.0001:
			# frappe.msgprint(self.total_invoice)
			# frappe.throw("Error,unallocated Payment Masih tersisa {}".format(self.unallocated_payment))
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')

	def on_submit(self):
		if self.unallocated_payment>0:
			# frappe.msgprint(self.total_invoice)
			frappe.throw("Error,unallocated Payment Masih ada {}".format(self.unallocated_payment))
		else:
			#			for cek in self.idr_payment:
				# if cek.mode_of_payment != "Cash":
					# frappe.throw("Silahkan Cek Transfer Bank Terlebih Dahulu")
				# else:				
			self.make_gl_entries()
				#posting Stock Ledger Post
			self.update_stock_ledger()
			self.repost_future_sle_and_gle()
				#update invoice
			for row in self.invoice_table:
				if row.allocated==row.outstanding:
					frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding-{} , invoice_status="Paid", gold_payment="{}" where name = "{}" """.format(row.allocated,self.name,row.gold_invoice))
				else:
					frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding-{} , gold_payment="{}" where name = "{}" """.format(row.allocated,self.name,row.gold_invoice))
			for row in self.customer_return:
				if row.allocated==row.outstanding:
					frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} , invoice_status="Paid" where name = "{}" """.format(row.allocated,row.invoice))
				else:
					frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} where name = "{}" """.format(row.allocated,row.invoice))
			if self.janji_bayar and self.total_idr_payment>0:
				janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
				if janji.status=="Pending":
					if janji.sisa_janji<=self.total_idr_payment : 
						frappe.db.sql("""update `tabJanji Bayar` set status="Lunas",total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
					else:
						frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
	def on_cancel(self):
		self.flags.ignore_links=True
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		#revert advance
		frappe.db.sql("""update `tabGL Entry` set  against_voucher_type=NULL,against_voucher=NULL where against_voucher_type="Gold Payment" and against_voucher="{}" """.format(self.name))
		#merge if needed
		gl_need_deleted=""
		patch={}
		for row in self.invoice_advance:
			if row.gold_allocated>0:
				gl_list=frappe.db.sql("""select name ,debit,credit,debit_in_account_currency,credit_in_account_currency from `tabGL Entry` where voucher_no="{}" and account="{}" and against_voucher_type=NULL and against_voucher=NULL and is_cancelled=0 """.format(row.customer_deposit,piutang_idr),as_list=1)
				for det in gl_list:
					if row.customer_deposit in patch:
						if gl_need_deleted!="":
							gl_need_deleted="""{},"{}" """.format(gl_need_deleted,det[0])
						else:
							gl_need_deleted=""" "{}" """.format(det[0])
						patch[row.customer_deposit]['need_patch']=1
						patch[row.customer_deposit]['debit']=flt(det[1])+patch[row.customer_deposit]['debit']
						patch[row.customer_deposit]['credit']=flt(det[2])+patch[row.customer_deposit]['credit']
						patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])+patch[row.customer_deposit]['debit_in_account_currency']
						patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])+patch[row.customer_deposit]['credit_in_account_currency']
					else:
						patch[row.customer_deposit]={}
						patch[row.customer_deposit]['need_patch']=0
						patch[row.customer_deposit]['debit']=flt(det[1])
						patch[row.customer_deposit]['name']=det[0]
						patch[row.customer_deposit]['credit']=flt(det[2])
						patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])
						patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])
		for row in self.gold_invoice_advance:
			if row.gold_allocated>0:
				gl_list=frappe.db.sql("""select name ,debit,credit,debit_in_account_currency,credit_in_account_currency from `tabGL Entry` where voucher_no="{}" and account="{}" and against_voucher_type=NULL and against_voucher=NULL and is_cancelled=0 """.format(row.customer_deposit,piutang_gold),as_list=1)
				for det in gl_list:
					if row.customer_deposit in patch:
						if gl_need_deleted!="":
							gl_need_deleted="""{},"{}" """.format(gl_need_deleted,det[0])
						else:
							gl_need_deleted=""" "{}" """.format(det[0])
						patch[row.customer_deposit]['need_patch']=1
						patch[row.customer_deposit]['debit']=flt(det[1])+patch[row.customer_deposit]['debit']
						patch[row.customer_deposit]['credit']=flt(det[2])+patch[row.customer_deposit]['credit']
						patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])+patch[row.customer_deposit]['debit_in_account_currency']
						patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])+patch[row.customer_deposit]['credit_in_account_currency']
					else:
						patch[row.customer_deposit]={}
						patch[row.customer_deposit]['need_patch']=0
						patch[row.customer_deposit]['debit']=flt(det[1])
						patch[row.customer_deposit]['name']=det[0]
						patch[row.customer_deposit]['credit']=flt(det[2])
						patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])
						patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])
		#delete merged GL
		if gl_need_deleted!="":
			frappe.db.sql("delete from `tabGL Entry` where name in ({})".format(gl_need_deleted),as_list=1)
			#update value gl merged
			for row in patch:
				if patch[row]['need_patch']==1:
					frappe.db.sql("""update `tabGL Entry` set debit={},credit={},debit_in_account_currency={},credit_in_account_currency={} where name="{}" """.format(patch[row]['debit'],patch[row]['credit'],patch[row]['debit_in_account_currency'],patch[row]['credit_in_account_currency'],patch[row]['name']),as_list=1)

		#update invoice
		for row in self.invoice_table:
			frappe.db.sql("""update `tabGold Invoice` set outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.allocated,row.gold_invoice))
		for row in self.customer_return:
			frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.allocated,row.invoice))
		if self.janji_bayar and self.total_idr_payment>0:
				janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
				if janji.status == "Lunas":
					frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} ,status="Pending", sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
				else:
					frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} , sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
	@frappe.whitelist()
	def get_gold_invoice(self):
		doc = frappe.db.get_list("Gold Invoice", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','posting_date','customer','outstanding','due_date','tutupan','total_bruto','grand_total'])
		for row in doc:
# <<<<<<< HEAD
			# frappe.msgprint(str(row))
#<<<<<<< HEAD
			# self.total_invoice = self.total_invoice + row.outstanding
#=======
			# self.total_invoice = flt(self.total_invoice) + flt(row.outstanding)
#>>>>>>> d96d2a3021f492f6640ef9afae4f1b2060304bfb
			# baris_baru = {
			# 	'gold_invoice':row.name,
			# 	'outstanding':row.outstanding,
			# 	'total':row.grand_total,
			# 	'due_date':row.due_date,
			# 	'total_bruto':row.total_bruto,
			# 	'tutupan':row.tutupan
			# }
			# self.append("invoice_table",baris_baru)
# =======
# >>>>>>> 26667448793274c7c08aea84fc8d69f96f0cebbf
			# frappe.msgprint(str(row))
			if row.outstanding and flt(row.outstanding)>0:
				if not self.total_invoice:
					self.total_invoice=0
				self.total_invoice = self.total_invoice + row.outstanding
				baris_baru = {
					'gold_invoice':row.name,
					'tanggal':row.posting_date,
					'customer':row.customer,
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
			if row.in_supplier==0:
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
   
	@frappe.whitelist()
	def gl_dict(self,cost_center,account,debit,credit,fiscal_years):
		return {
										"posting_date":self.posting_date,
										"account":account,
										"party_type":"",
										"party":"",
										"cost_center":cost_center,
										"debit":debit,
										"credit":credit,
										"account_currency":"IDR",
										"debit_in_account_currency":debit,
										"credit_in_account_currency":credit,
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
	def gl_dict_with_sup(self,cost_center,account,debit,credit,fiscal_years,sup):
		return {
										"posting_date":self.posting_date,
										"account":account,
										"party_type":"Supplier",
										"party":sup,
										"cost_center":cost_center,
										"debit":debit,
										"credit":credit,
										"account_currency":"IDR",
										"debit_in_account_currency":debit,
										"credit_in_account_currency":credit,
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
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi

		gl_entries = []
		gl = {}
		
		gl_piutang = []
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		#mapping allocated
		inv_payment_map = {}
		for row in self.invoice_table:
			inv_payment_map[row.gold_invoice] = row.allocated
			
		for row in self.customer_return:
			inv_payment_map[row.invoice] = row.allocated

		nilai_selisih_kurs = 0
		#hitung selisih kurs untuk DP
		for row in self.gold_invoice_advance:
			nilai_selisih_kurs=nilai_selisih_kurs+(row.gold_allocated*(self.tutupan-row.tutupan))
		# distribute total gold perlu bagi per invoice
		sisa= self.total_payment
		credit=0
		debit=0
		for row in self.invoice_table:
			if sisa>0 and row.allocated>0:
				payment=row.allocated
				if sisa < row.allocated:
					payment=sisa

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
		#		credit=credit+(payment*row.tutupan)
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*payment)
		#frappe.msgprint("Invoice Payment credit = {} , debit = {}".format(credit,debit))
		for row in self.customer_return:
			if sisa>0 and row.allocated>0:
				payment=row.allocated
				if sisa<row.allocated:
					payment = sisa
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
#				credit=credit+(payment*row.tutupan)
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*payment)
		roundoff=0
#		frappe.msgprint("Customer Return credit = {} , debit = {}".format(credit,debit))
		for row in gl_piutang:
			roundoff=roundoff+row['debit']-row['credit']
			gl_entries.append(frappe._dict(row))
		#perlu check selisih kurs dari tutupan
		#lebih dr 0 itu debit
		dsk=0
		csk=0
		if nilai_selisih_kurs!=0:
			if nilai_selisih_kurs<0:
				dsk=nilai_selisih_kurs*-1
			else:
				csk=nilai_selisih_kurs
			gl[selisih_kurs]=self.gl_dict(cost_center,selisih_kurs,dsk,csk,fiscal_years)
		#adnvace GL
		adv=[]
		for row in self.invoice_advance:
			advance_split=[]
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.idr_left >=row.idr_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left={} where name="{}" """.format(deposit.idr_left -row.idr_allocated,row.customer_deposit),as_list=1)
				#update GL for payment
				#if pembayaran di gunakan full
				if deposit.idr_left ==row.idr_allocated:
					frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Payment",against_voucher="{}" where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,row.customer_deposit,piutang_idr),as_list=1)
				else:
				#if split needed
					frappe.db.sql("""update `tabGL Entry` set debit={0},debit_in_account_currency={0} where voucher_no="{1}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{2}" and is_cancelled=0""".format(deposit.idr_left -row.idr_allocated,row.customer_deposit,piutang_idr),as_list=1)
					adv.append({
									"posting_date":self.posting_date,
									"account":piutang_idr,
									"party_type":"Customer",
									"party":row.customer,
									"cost_center":cost_center,
									"credit":0,
									"debit":row.idr_allocated,
									"account_currency":"IDR",
									"credit_in_account_currency":0,
									"debit_in_account_currency":row.idr_allocated,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"against_voucher_type":"Gold Payment",
									"voucher_no":row.customer_deposit,
									"against_voucher":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									})
		for row in self.gold_invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.gold_left >=row.gold_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set  gold_left={} where name="{}" """.format(deposit.gold_left -row.gold_allocated,row.customer_deposit),as_list=1)
				#update GL for payment
				#if pembayaran di gunakan full
				if deposit.gold_left ==row.gold_allocated:
					frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Payment",against_voucher="{}" where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,row.customer_deposit,piutang_gold),as_list=1)
				else:
				#if split needed
					frappe.db.sql("""update `tabGL Entry` set debit={},debit_in_account_currency={} where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format((deposit.gold_left -row.gold_allocated)*deposit.tutupan,deposit.gold_left -row.gold_allocated,row.customer_deposit,piutang_gold),as_list=1)
					adv.append({
									"posting_date":deposit.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":row.customer,
									"cost_center":cost_center,
									"credit":0,
									"debit":row.gold_allocated*deposit.tutupan,
									"account_currency":"IDR",
									"credit_in_account_currency":0,
									"debit_in_account_currency":row.gold_allocated,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"against_voucher_type":"Gold Payment",
									"voucher_no":row.customer_deposit,
									"against_voucher":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									})
		for row in adv:
			gl_entries.append(frappe._dict(row))
		#	credit=credit+csk
		#	debit=debit+dsk
		#frappe.msgprint("Selisih Kurs credit = {} , debit = {}".format(credit,debit))
		#BONUS,DISCOUNT,WRITEOFF
		if self.bonus>0:
			bonus_payment = frappe.db.get_single_value('Gold Selling Settings', 'bonus_payment')
			gl[bonus_payment]=self.gl_dict(cost_center,bonus_payment,self.bonus*self.tutupan,0,fiscal_years)
			
		#	debit=debit+(self.bonus*self.tutupan)
		#	frappe.msgprint("Bonus credit = {} , debit = {}".format(credit,debit))
		if self.discount_amount>0:
			discount_payment = frappe.db.get_single_value('Gold Selling Settings', 'discount_payment')
			gl[discount_payment]= self.gl_dict(cost_center,discount_payment,self.discount_amount*self.tutupan,0,fiscal_years)
			
		if self.jadi_deposit>0:
			deposit = frappe.db.get_single_value('Gold Selling Settings', 'payment_deposit_coa')
			gl[deposit]= self.gl_dict(cost_center,deposit,0,self.jadi_deposit*self.tutupan,fiscal_years)
			# frappe.msgprint(deposit)
			#create deposit
			depo = frappe.new_doc("Customer Deposit")
			depo.customer = self.customer
			depo.customer_group = self.customer_group
			depo.territory = self.territory
			depo.subcustomer = self.subcustomer
			depo.warehouse = self.warehouse
			depo.posting_date = self.posting_date
			depo.deposit_type="Emas"
			depo.tutupan=self.tutupan
			depo.sales_bundle=self.sales_bundle
			depo.deposit_payment=1
			depo.gold_payment=self.name
			depo.total_gold_deposit=self.jadi_deposit
			depo.gold_left=self.jadi_deposit
			# frappe.msgprint(depo)
			depo.flags.ignore_permissions = True
			depo.save()
			depo.submit()
		#	debit=debit+(self.discount_amount*self.tutupan)
		#	frappe.msgprint("Discount credit = {} , debit = {}".format(credit,debit))
		if self.write_off!=0:
			if self.write_off>0:
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,self.write_off*self.tutupan,0,fiscal_years)
			else:
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,0,self.write_off*self.tutupan*-1,fiscal_years)
		#	debit=debit+(self.write_off*self.tutupan)
		#	frappe.msgprint("Writeoff credit = {} , debit = {}".format(credit,debit))
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if self.total_gold_payment>0:
			warehouse_value=0
			titip={}
			supplier_list=[]
			for row in self.stock_payment:
				if row.in_supplier==1:
					if row.supplier in supplier_list:
						titip[row.supplier]=row.amount
						supplier_list.append(row.supplier)
					else:
						titip[row.supplier]=titip[row.supplier]+row.amount
				else :
					warehouse_value=warehouse_value+row.amount
			if warehouse_value>0:
				warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
				gl[warehouse_account]=self.gl_dict(cost_center,warehouse_account,self.total_gold_deposit*self.tutupan,0,fiscal_years)
			if len(supplier_list)>0:
				uang_buat_beli_emas= frappe.db.get_single_value('Gold Selling Settings', 'uang_buat_beli_emas')
				for sup in supplier_list:
					gl[sup]=self.gl_dict_with_sup(cost_center,uang_buat_beli_emas,titip[sup],0,fiscal_years,sup)
			# warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
			# gl[warehouse_account]={
			# 	"posting_date":self.posting_date,
			# 	"account":warehouse_account,
			# 	"party_type":"",
			# 	"party":"",
			# 	"cost_center":cost_center,
			# 	"debit":self.total_gold_payment*self.tutupan,
			# 	"credit":0,
			# 	"account_currency":"IDR",
			# 	"debit_in_account_currency":self.total_gold_payment*self.tutupan,
			# 	"credit_in_account_currency":0,
			# 	#"against":"4110.000 - Penjualan - L",
			# 	"voucher_type":"Gold Payment",
			# 	"voucher_no":self.name,
			# 	#"remarks":"",
			# 	"is_opening":"No",
			# 	"is_advance":"No",
			# 	"fiscal_year":fiscal_years,
			# 	"company":self.company,
			# 	"is_cancelled":0
			# }
		#	debit=debit+(self.total_gold_payment*self.tutupan)
		#	frappe.msgprint("Gold Payment credit = {} , debit = {}".format(credit,debit))
		#untuk payment IDR
		if self.total_idr_payment>0:
			#journal IDR nya aja
			for row in self.idr_payment:
				account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
				if account in gl:
					if  row.amount >0:
						gl[account]['debit']=gl[account]['debit']+row.amount
						gl[account]['debit_in_account_currency']=gl[account]['debit']
					else:
						gl[account]['credit']=gl[account]['credit']-row.amount
						gl[account]['credit_in_account_currency']=gl[account]['credit']
				else:
					if row.amount >0:
						gl[account]=self.gl_dict(cost_center,account,row.amount,0,fiscal_years)
					else:
						gl[account]=self.gl_dict(cost_center,account,0,-1*row.amount,fiscal_years)
#				debit=debit+row.amount
#			frappe.msgprint("IDR Payment credit = {} , debit = {}".format(credit,debit))
		#roundoff=0
		for row in gl:
		#	frappe.msgprint("RO {} Account {} has {} and {}".format(roundoff,gl[row]['account'],gl[row]['debit'],gl[row]['credit']))
			roundoff=roundoff+gl[row]['debit']-gl[row]['credit']
			gl_entries.append(frappe._dict(gl[row]))
		#add roundoff
		if roundoff!=0:
			roundoff_coa=frappe.db.get_value('Company', self.company, 'round_off_account')
			if roundoff>0:
				gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,0,roundoff,fiscal_years)
#				debit=debit+roundoff
			else:
				gl[roundoff_coa]=gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,roundoff*-1,0,fiscal_years)
				
#				credit=credit+roundoff
			gl_entries.append(frappe._dict(gl[roundoff_coa]))
#			frappe.msgprint("Round Off credit = {} , debit = {}".format(credit,debit))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries
