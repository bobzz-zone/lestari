# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.controllers.stock_controller import StockController
from frappe.utils import flt
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
			self.terima_barang=0
			if self.source and self.total_value_converted>0:
				item_ct = frappe.db.get_single_value('Gold Selling Settings', 'item_ct')
				qty = self.total_value_converted/self.tutupan
				self.append("stock_deposit",{"item":item_ct,"rate":100,"qty":qty,"amount":qty})
				self.total_gold_deposit=qty
				self.gold_left=qty
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
	def on_submit(self):
		if not self.account_piutang:
			self.account_piutang = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		self.make_gl_entries()
		#posting Stock Ledger Post
		if self.terima_barang==1 and self.is_convert==0:
			self.update_stock_ledger()
			self.repost_future_sle_and_gle()
		if self.is_convert==1:
			for row in  self.source:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left-{} where name="{}" """.format(row.convert,row.customer_deposit),as_list=1)
		# if self.janji_bayar and self.total_idr_deposit>0:
		# 		janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
		# 		if janji.status=="Pending":
		# 			if janji.sisa_janji<=self.total_idr_deposit : 
		# 				frappe.db.sql("""update `tabJanji Bayar` set status="Lunas",total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(self.total_idr_deposit,self.janji_bayar))
		# 			else:
		# 				frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(self.total_idr_deposit,self.janji_bayar))
		if self.list_janji_bayar and self.total_idr_deposit>0:
			for row in self.list_janji_bayar:
				deposit = self.total_idr_deposit #5,938,340,461.00
				# frappe.msgprint(row.janji_bayar)
				# frappe.msgprint(deposit)
				if deposit > 0:
					janji=frappe.get_doc("Janji Bayar",row.janji_bayar)
					if janji.status=="Pending":
						if janji.sisa_janji<=deposit : 
							frappe.db.sql("""update `tabJanji Bayar` set status="Lunas", total_terbayar = {0}, sisa_janji=0 where name = "{1}" """.format(janji.total_bayar,row.janji_bayar))
							frappe.db.sql("""UPDATE `tabPembayaran Janji Bayar` SET idr_janji_bayar = {2}, sisa_janji = {3}, status_janji = "{4}",allocated_janji = {0} where name = "{1}" """.format(janji.sisa_janji,row.name,janji.total_bayar, 0,"Lunas"))
						else:
							frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(deposit,row.janji_bayar))
							frappe.db.sql("""UPDATE `tabPembayaran Janji Bayar` SET idr_janji_bayar = {2}, sisa_janji = {3},allocated_janji = {0} where name = "{1}" """.format(deposit,row.name,row.idr_janji_bayar + row.allocated_janji, (row.total_janji_bayar - row.allocated_janji)))
					deposit = deposit - janji.sisa_janji # 5,938,340,461.00 - 5,451,000,000.00 = 487,340,461.00
		self.reload()
     
	def on_cancel(self):
		self.flags.ignore_links=True
		if self.idr_left !=self.total_idr_deposit or self.gold_left != self.total_gold_deposit:
			frappe.throw("Deposit ini sudah terpakai tidak bisa di cancel")
		self.make_gl_entries()
		if self.terima_barang==1 and self.is_convert==0:
			self.update_stock_ledger()
			self.repost_future_sle_and_gle()
		if self.is_convert==1:
			for row in  self.source:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left+{} where name="{}" """.format(row.convert,row.customer_deposit),as_list=1)
		if self.janji_bayar and self.total_idr_deposit>0:
				janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
				if janji.status == "Lunas":
					frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} ,status="Pending", sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_deposit,self.janji_bayar))
				else:
					frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} , sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_deposit,self.janji_bayar))
		if self.list_janji_bayar and self.total_idr_deposit>0:
			for row in self.list_janji_bayar:
					janji=frappe.get_doc("Janji Bayar",row.janji_bayar)
					if janji.status == "Lunas":
						frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} ,status="Pending", sisa_janji=sisa_janji+{0} where name = "{1}" """.format(row.allocated_janji,row.janji_bayar))
					else:
						frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} , sisa_janji=sisa_janji+{0} where name = "{1}" """.format(row.allocated_janji,row.janji_bayar))

     
	@frappe.whitelist()
	def get_janji_bayar(self):
		self.list_janji_bayar=[]
		doc = frappe.db.get_list("Janji Bayar", filters={"customer": self.customer, "status":"Pending", 'docstatus':1, 'jenis_janji':"Deposit"}, fields=['name','tanggal_janji','customer','gold_invoice','total_bayar','total_terbayar','sisa_janji','status'], order_by="name")
		# frappe.msgprint(str(doc))
		total_idr_payment = 0
		if len(doc) > 0:
			for row in doc:
				if len(doc) == 1:
					self.janji_bayar = row.name
					self.sisa_janji = row.sisa_janji
					self.total_janji = row.total_bayar
				baris_baru = {
					'janji_bayar':row.name,
					'no_invoice':row.gold_invoice,
					'customer':row.customer,
					'tanggal_janji':row.tanggal_janji,
					'total_janji_bayar':row.total_bayar,
					'idr_janji_terbayar':row.total_terbayar,
					'sisa_janji':row.sisa_janji,
					'status_janji':row.status
				}
				self.append("list_janji_bayar",baris_baru)
    
	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		for row in self.stock_deposit:
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
			# frappe.msgprint(str(gl_entries))
		
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
				piutang_gold = self.piutang_gold
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 :
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
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
										"voucher_type":"Customer Deposit",
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
										"voucher_type":"Customer Deposit",
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
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		if self.is_convert==0:
			#1 untuk GL untuk piutang Gold
			if not self.total_gold_deposit:
				self.total_gold_deposit = 0
			if flt(self.total_gold_deposit) > 0 and self.deposit_type=="Emas":
				piutang_gold = self.piutang_gold
				# frappe.msgprint(str(piutang_gold))
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
				if self.deposit_payment==1:
					depo_account = frappe.db.get_single_value('Gold Selling Settings', 'payment_deposit_coa')
					# frappe.msgprint(str(depo_account))
					gl[depo_account]=self.gl_dict(cost_center,depo_account,self.total_gold_deposit*self.tutupan,0,fiscal_years)

				else:
					warehouse_value=0
					titip={}
					supplier_list=[]
					for row in self.stock_deposit:
						if row.in_supplier==1:
							if row.supplier in supplier_list:
								titip[row.supplier] += row.amount
							else:
								titip[row.supplier] = row.amount
								supplier_list.append(row.supplier)
						else :
							warehouse_value=warehouse_value+row.amount
					# frappe.throw(str(titip))
					# frappe.msgprint(str(warehouse_value))
					if warehouse_value>0:
						self.terima_barang=1
						warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
						gl[warehouse_account]=self.gl_dict(cost_center,warehouse_account,self.total_gold_deposit*self.tutupan,0,fiscal_years)
						# frappe.msgprint(str(gl[warehouse_account]))
					if len(supplier_list)>0:
						uang_buat_beli_emas= frappe.db.get_single_value('Gold Selling Settings', 'uang_buat_beli_emas')
						for sup in supplier_list:
							gl[sup]=self.gl_dict_with_sup(cost_center,uang_buat_beli_emas,titip[sup]*self.tutupan,0,fiscal_years,sup)
				# elif self.terima_barang==1:
				# else:
				# 	uang_buat_beli_emas= frappe.db.get_single_value('Gold Selling Settings', 'uang_buat_beli_emas')
				# 	gl[uang_buat_beli_emas]=gl_dict(cost_center,uang_buat_beli_emas,self.total_gold_deposit*self.tutupan,0,fiscal_years)

			#untuk deposit IDR
			if self.total_idr_deposit and self.total_idr_deposit > 0 and self.deposit_type == "IDR":
				piutang_idr = self.account_piutang
				
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
				if self.deposit_payment==1:
					depo_account = frappe.db.get_single_value('Gold Selling Settings', 'payment_deposit_coa')
					# frappe.msgprint(str(depo_account))
					gl[depo_account]=self.gl_dict(cost_center,depo_account,self.total_idr_deposit,0,fiscal_years)
				for row in self.idr_deposit:
					account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
					if account in gl:
						gl[account]['debit']=gl[account]['debit']+row.amount
						gl[account]['debit_in_account_currency']=gl[account]['debit']
					else:
						gl[account]=self.gl_dict(cost_center,account,row.amount,0,fiscal_years)				
		else:
			if self.deposit_type!="Emas":
				frappe.throw("Conversion hanya bisa untuk Deposit Rupiah menjadi emas")
			if self.total_value_converted>0:
				piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
				piutang_gold = self.piutang_gold
				uang_buat_beli_emas = frappe.db.get_single_value('Gold Selling Settings', 'uang_buat_beli_emas')
				for row in self.source:
					gl[row.customer_deposit]={
									"posting_date":self.posting_date,
									"account":piutang_idr,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"credit":0,
									"debit":row.convert,
									"account_currency":"IDR",
									"credit_in_account_currency":0,
									"debit_in_account_currency":row.convert,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"against_voucher_type":"Customer Deposit",
									"voucher_no":self.name,
									"against_voucher":row.customer_deposit,
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
								"debit":0,
								"credit":self.total_value_converted,
								"account_currency":"GOLD",
								"debit_in_account_currency":0,
								"credit_in_account_currency":self.total_value_converted/self.tutupan,
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
		# frappe.throw(str(gl))
		gl_entries=[]
		against_debit=""
		against_credit=""
		# frappe.msgprint(str(gl))
		for row in gl:
			if gl[row]["debit"]>0:
				if str(gl[row]["account"]) not in against_credit:
					against_credit="{} ,{}".format(against_credit,gl[row]["account"])
			else:
				if str(gl[row]["account"]) not in against_debit:
					against_debit="{} ,{}".format(against_debit,gl[row]["account"])
		for row in gl:
			if gl[row]["debit"]>0:
				gl[row]["against"]=against_debit
			else:
				gl[row]["against"]=against_credit
			gl_entries.append(frappe._dict(gl[row]))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries
@frappe.whitelist()
def get_idr_advance(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select name , idr_left from `tabCustomer Deposit` where name LIKE %(txt)s and idr_left>0 and deposit_type="IDR" and docstatus=1 and (customer=%(customer)s or subcustomer=%(subcustomer)s ) """,
		{"customer": filters.get("customer", ""),"subcustomer": filters.get("subcustomer", ""), "txt": "%" + txt + "%"},
	)
@frappe.whitelist()
def get_gold_advance(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select name , gold_left from `tabCustomer Deposit` where name LIKE %(txt)s and gold_left>0 and deposit_type="Emas" and docstatus=1 and (customer=%(customer)s or subcustomer=%(subcustomer)s ) """,
		{"customer": filters.get("customer", ""),"subcustomer": filters.get("subcustomer", ""), "txt": "%" + txt + "%"},
	)
@frappe.whitelist()
def get_deposit_outstanding(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select name ,deposit_type,idr_left , gold_left from `tabCustomer Deposit` where name LIKE %(txt)s and (idr_left>0 or gold_left>0) and docstatus=1 and (customer=%(customer)s or subcustomer=%(subcustomer)s ) """,
		{"customer": filters.get("customer", ""),"subcustomer": filters.get("subcustomer", ""), "txt": "%" + txt + "%"},
	)
