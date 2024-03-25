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

form_grid_templates = {"invoice_table": "templates/item_grid.html"}
#need to check GL
#need check write off dan deposit
class GoldPayment(StockController):
	def validate(self):
		if self.list_janji_bayar:
			if len(self.list_janji_bayar) == 1:
				for row in self.list_janji_bayar:
					self.janji_bayar = row.janji_bayar
			else:
				frappe.msgprint("Janji Bayar Lebih dari 1")

		if self.idr_payment:
			for row in self.idr_payment:
				type_payment = frappe.db.get_value("Mode of Payment", row.mode_of_payment, "is_sales")
				if type_payment < 1:
					frappe.throw("Mode Pembayaran Salah")
				

		total = self.total_idr_payment
		for row in self.list_janji_bayar:
			if total == 0 :
				continue
			if total>row.sisa_janji:
				row.allocated_janji = row.sisa_janji
			else:
				row.allocated_janji = total
			total=total-row.allocated_janji
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
		# frappe.msgprint("PY:"+self.jadi_deposit)

	def on_submit(self):
		if self.unallocated_payment>0.001:
			# frappe.msgprint(self.total_invoice)
			frappe.throw("Error,unallocated Payment Masih ada {}".format(self.unallocated_payment))
		else:
			self.status_document="Submitted"
			##			for cek in self.idr_payment:
				# if cek.mode_of_payment != "Cash":
					# frappe.throw("Silahkan Cek Transfer Bank Terlebih Dahulu")
				# else:
			self.make_gl_entries()
				#posting Stock Ledger Post
			self.update_stock_ledger()
			self.repost_future_sle_and_gle()
				#stock return transfer
			total_cpr24k = 0
			if self.stock_return_transfer:
				cpr = frappe.new_doc("Customer Payment Return")
				cpr.no_pembayaran = self.name
				cpr.no_nota = self.invoice_table[0].gold_invoice
				cpr.customer = self.customer
				cpr.sales_bundle = self.sales_bundle
				for row in self.stock_return_transfer:
					total_cpr24k = total_cpr24k + row.amount
					baris_baru = {
						'item':row.item,
						'qty':row.bruto,
						'rate':row.rate,
						'tutupan':self.tutupan,
						'voucher_type': self.doctype,
						'voucher_no': self.name,
						'no_document': row.no_parent,
						'amount': row.amount
					}
					cpr.append('items',baris_baru)
					frappe.db.sql(""" UPDATE `tabStock Return Transfer Details` SET is_out = {} where name = "{}" """.format(1,row.no_doc))
				cpr.total = total_cpr24k
				cpr.outstanding = total_cpr24k
				cpr.flags.ignore_permissions = True
				cpr.submit()
				
				#update invoice
			if self.jadi_deposit>0:
				piutang_gold = self.piutang_gold
				depo = frappe.new_doc("Customer Deposit")
				depo.customer = self.customer
				depo.customer_group = self.customer_group
				depo.territory = self.territory
				depo.subcustomer = self.subcustomer
				depo.warehouse = self.warehouse
				depo.posting_date = self.posting_date
				depo.deposit_type= self.type_deposit
				depo.type_emas=self.type_emas
				depo.tutupan=self.tutupan
				depo.sales_bundle=self.sales_bundle
				depo.deposit_payment=1
				depo.gold_payment=self.name
				if self.type_deposit == "Emas":
					depo.total_gold_deposit=self.jadi_deposit
					depo.gold_left=self.jadi_deposit
				else:
					depo.total_idr_deposit=self.jadi_deposit * self.tutupan
					depo.idr_left=self.jadi_deposit * self.tutupan
				# depo.gold_type=self.type_emas
				depo.type_emas=self.type_emas
				depo.piutang_gold = piutang_gold
				depo.account_piutang=frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
				# frappe.msgprint(depo)
				depo.flags.ignore_permissions = True
				# depo.save()
				depo.submit()
				#depo.submit()
				# frappe.msgprint("Customer Deposit {} Telah Terbuat".format(depo.name))
			for row in self.invoice_table:
				if row.allocated==row.outstanding and row.tax_allocated==row.outstanding_tax:
					frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak - {} ,outstanding=outstanding-{} , invoice_status="Paid", gold_payment="{}" where name = "{}" """.format(row.tax_allocated,row.allocated,self.name,row.gold_invoice))
				else:
					frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak - {} , outstanding=outstanding-{} , gold_payment="{}" where name = "{}" """.format(row.tax_allocated,row.allocated,self.name,row.gold_invoice))
			for row in self.customer_return:
				if row.allocated==row.outstanding:
					frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} , invoice_status="Paid" where name = "{}" """.format(row.allocated,row.invoice))
				else:
					frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding-{} where name = "{}" """.format(row.allocated,row.invoice))
			if self.janji_bayar and self.total_idr_payment>0:
				# janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
				# if janji.status=="Pending":
				# 	if janji.sisa_janji<=self.total_idr_payment : 
				# 		frappe.db.sql("""update `tabJanji Bayar` set status="Lunas",total_terbayar=total_terbayar+sisa_janji , sisa_janji=0 where name = "{0}" """.format(self.janji_bayar))
				# 	else:
				# 		frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar+{0} , sisa_janji=sisa_janji-{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
				for row in self.list_janji_bayar:
					deposit = self.total_idr_payment #5,938,340,461.00
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
		self.status_document="Cancelled"
		piutang_gold = self.piutang_gold
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		if self.list_janji_bayar and self.total_idr_payment>0:
			for row in self.list_janji_bayar:
					janji=frappe.get_doc("Janji Bayar",row.janji_bayar)
					if janji.status == "Lunas":
						frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} ,status="Pending", sisa_janji=sisa_janji+{0} where name = "{1}" """.format(row.allocated_janji,row.janji_bayar))
					else:
						frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} , sisa_janji=sisa_janji+{0} where name = "{1}" """.format(row.allocated_janji,row.janji_bayar))
		#revert advance
		frappe.db.sql("""update `tabGL Entry` set  against_voucher_type=NULL,against_voucher=NULL where against_voucher_type="Gold Payment" and against_voucher="{}" """.format(self.name))
		#merge if needed
		if self.stock_return_transfer:
			doc = frappe.get_doc("Customer Payment Return", filters={"no_pembayaran":self.name})
			doc.flags.ignore_permissions = True
			doc.cancel()
			for row in self.stock_return_transfer:
				frappe.db.sql(""" UPDATE `tabStock Return Transfer Details SET is_out = {} where name = {} """.format(0,row.no_doc))

		gl_need_deleted=""
		patch={}
		for row in self.invoice_advance:
			if row.idr_allocated>0:
				#reset idr left
				frappe.db.sql("update `tabCustomer Deposit` set idr_left=idr_left+{} where name='{}'".format(row.idr_allocated,row.customer_deposit),as_list=1)
				gl_list=frappe.db.sql("""select name ,debit,credit,debit_in_account_currency,credit_in_account_currency from `tabGL Entry` where voucher_no="{}" and account="{}" and against_voucher_type=NULL and against_voucher=NULL and is_cancelled=0 """.format(row.customer_deposit,row.account_piutang),as_list=1)
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
				#reset gold left
				frappe.db.sql("update `tabCustomer Deposit` set gold_left=gold_left+{} where name='{}'".format(row.gold_allocated,row.customer_deposit),as_list=1)
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
			frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak+{} ,outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.tax_allocated,row.allocated,row.gold_invoice))
		for row in self.customer_return:
			frappe.db.sql("""update `tabCustomer Payment Return` set outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.allocated,row.invoice))
		# if self.janji_bayar and self.total_idr_payment>0:
		# 		janji=frappe.get_doc("Janji Bayar",self.janji_bayar)
		# 		if janji.status == "Lunas":
		# 			frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} ,status="Pending", sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
		# 		else:
		# 			frappe.db.sql("""update `tabJanji Bayar` set total_terbayar=total_terbayar-{0} , sisa_janji=sisa_janji+{0} where name = "{1}" """.format(self.total_idr_payment,self.janji_bayar))
	@frappe.whitelist()
	def get_janji_bayar(self):
		doc = frappe.db.get_list("Janji Bayar", filters={"customer": self.customer, "status":"Pending", 'docstatus':1, 'jenis_janji':"Pembayaran"}, fields=['name','tanggal_janji','customer','gold_invoice','total_bayar','total_terbayar','sisa_janji','status'])
		total_idr_payment = 0
		for row in doc:
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
			baris_baru = {
				'mode_of_payment': "Kas Sales",
				'amount': row.sisa_janji
			}
			total_idr_payment += row.sisa_janji
			self.append("idr_payment",baris_baru)
		self.total_idr_payment += flt(total_idr_payment) 
		self.total_idr_gold += flt(total_idr_payment) / flt(self.tutupan)
		self.total_payment += flt(total_idr_payment) / flt(self.tutupan)
		self.unallocated_payment += flt(total_idr_payment) / flt(self.tutupan)
			
	@frappe.whitelist()
	def get_gold_invoice(self):
		#reset before add
		self.invoice_table=[]
		self.gold_invoice_advance=[]
		self.customer_return=[]
		self.invoice_advance=[]
		self.total_gold = 0
		# doc = frappe.db.get_list("Gold Invoice", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','posting_date','customer','subcustomer','enduser','outstanding','due_date','tutupan','total_bruto','grand_total'])
		doc = frappe.db.sql("""
                      SELECT
                      name,
                      posting_date,
                      customer,
                      subcustomer,
                      enduser,
                      outstanding,
                      due_date,
                      tutupan,
                      total_bruto,
                      grand_total,
                      sisa_pajak
                      FROM `tabGold Invoice`
                      WHERE invoice_status = "Unpaid"
                      and docstatus = 1
                      and (
                      customer = "{0}"
                      or customer = "{1}" )
					  and type_emas = "{2}"
                      """.format(self.customer, self.subcustomer, self.type_emas),as_dict=1)
		# frappe.msgprint(str(doc))
		if self.tutupan > 0:
			tutupan = self.tutupan
		else:
			tutupan = frappe.db.sql("""
                        SELECT nilai
						FROM `tabGold Rates`
						WHERE nilai > 0
						AND DATE <= CURDATE() 
						ORDER BY DATE DESC
						LIMIT 1
                           """, as_dict=1)
			# frappe.msgprint(str())
			tutupan = tutupan[0].nilai
			self.tutupan = flt(tutupan)
		for row in doc:
			# frappe.msgprint(str(row))
			if row.outstanding and flt(row.outstanding)>0:
				if not self.total_invoice:
					self.total_invoice=0
				self.total_invoice = self.total_invoice + row.outstanding
				baris_baru = {
					'gold_invoice':row.name,
					'tanggal':row.posting_date,
					'customer':row.customer,
					'sub_customer':row.subcustomer,
					'end_user':row.enduser,
					'outstanding':row.outstanding,
					'total':row.grand_total,
					'due_date':row.due_date,
					'total_bruto':row.total_bruto,
					'tutupan':row.tutupan,
					'outstanding_tax':row.sisa_pajak
				}
				self.append("invoice_table",baris_baru)
		list_cpr = frappe.db.get_list("Customer Payment Return", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','outstanding','due_date','tutupan','total'])
		if not self.total_invoice:
			self.total_invoice=0
		for row in list_cpr:
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
		# list_srt = frappe.db.get_list("Stock Return Transfer", filters={"type":"Keluar", "docstatus":1})
		# # total24k = 0
		# for row in list_srt:
		# 	doc = frappe.get_doc("Stock Return Transfer", row.name)
		# 	for col in doc.transfer_details:
		# 		if self.customer == col.customer or self.customer == col.sub_customer:
		# 			if col.is_out == 0:
		# 				# frappe.msgprint(row.name)
		# 				# frappe.msgprint(col.name)
		# 				# total24k = total24k + col.berat
		# 				baris_baru_item = {
		# 					'item':col.item,
		# 					'customer': col.customer,
		# 					'sub_customer': col.sub_customer,
		# 					'bruto':col.berat,
		# 					'no_parent' : row.name,
		# 					'no_doc': col.name
		# 				}
		# 				self.append("stock_return_transfer",baris_baru_item)
				
		# self.total_24k_return = total24k
		#lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_idr_advance
		#lestari.gold_selling.doctype.customer_deposit.customer_deposit.get_gold_advance
		total_advance = 0
		#if self.type_payment=="IDR":
		list_deposit=frappe.db.sql("""select name , idr_left ,account_piutang,posting_date,customer from `tabCustomer Deposit` where idr_left>0 and deposit_type="IDR" and docstatus=1 and (customer="{}" or subcustomer="{}" ) and type_emas ="{}" """.format(self.customer,self.subcustomer,self.type_emas),as_dict=1)
		total_idr_in_gold = 0
		for row in list_deposit:
			# frappe.msgprint(str(row))
			total_idr_in_gold += flt(row.idr_left)
			baris_baru = {
				'customer_deposit':row.name,
				'idr_deposit':row.idr_left,
				'idr_allocated':row.idr_left,
				'date':row.posting_date,
				'customer':row.customer,
				'account_piutang':row.account_piutang
			}
			# frappe.msgprint(str(total_idr_in_gold))
			self.append("invoice_advance",baris_baru)
		if total_idr_in_gold > 0:
			# frappe.msgprint(str(tutupan[0]))
			total_idr_in_gold = flt(total_idr_in_gold) / flt(tutupan)
			self.total_idr_in_gold = total_idr_in_gold
			total_advance += total_idr_in_gold
		#if self.type_payment=="Gold":
		list_deposit=frappe.db.sql("""select name , gold_left ,tutupan,posting_date,customer from `tabCustomer Deposit` where gold_left>0 and deposit_type="Emas" and docstatus=1 and (customer="{}" or subcustomer="{}" ) and type_emas ="{}" """.format(self.customer,self.subcustomer,self.type_emas),as_dict=1)
		total_gold = 0
		for row in list_deposit:
			# frappe.msgprint(str(row))
			total_gold += row.gold_left
			baris_baru = {
				'customer_deposit':row.name,
				'gold_deposit':row.gold_left,
				'gold_allocated':row.gold_left,
				'date':row.posting_date,
				'customer':row.customer,
				'tutupan':row.tutupan
			}
			self.append("gold_invoice_advance",baris_baru)
		self.total_gold = total_gold
		total_advance += total_gold
#		list_deposit=frappe.db.sql("""select name , idr_left ,account_piutang,posting_date,customer from `tabCustomer Deposit` where idr_left>0 and deposit_type="IDR" and docstatus=1 and (customer="{}" or subcustomer="{}" ) """.format(self.customer,self.subcustomer),as_dict=1)
#		total_advance = 0
#		total_idr_in_gold = 0
#		for row in list_deposit:
#			# frappe.msgprint(str(row))
#			total_idr_in_gold += flt(row.idr_left)
#			baris_baru = {
#				'customer_deposit':row.name,
#				'idr_deposit':row.idr_left,
#				'idr_allocated':row.idr_left,
#				'date':row.posting_date,
#				'customer':row.customer,
#				'account_piutang':row.account_piutang
#			}
#			# frappe.msgprint(str(total_idr_in_gold))
#			self.append("invoice_advance",baris_baru)
#		if total_idr_in_gold > 0:
#			# frappe.msgprint(str(tutupan[0]))
#			total_idr_in_gold = flt(total_idr_in_gold) / flt(tutupan)
#			self.total_idr_in_gold = total_idr_in_gold
#			total_advance += total_idr_in_gold
#		list_deposit=frappe.db.sql("""select name , gold_left ,tutupan,posting_date,customer from `tabCustomer Deposit` where gold_left>0 and deposit_type="Emas" and docstatus=1 and (customer="{}" or subcustomer="{}" ) """.format(self.customer,self.subcustomer),as_dict=1)
#		total_gold = 0
#		for row in list_deposit:
#			# frappe.msgprint(str(row))
#			total_gold += row.gold_left
#			baris_baru = {
#				'customer_deposit':row.name,
#				'gold_deposit':row.gold_left,
#				'gold_allocated':row.gold_left,
#				'date':row.posting_date,
#				'customer':row.customer,
#				'tutupan':row.tutupan
#			}
#			self.append("gold_invoice_advance",baris_baru)
#		self.total_gold = total_gold
#		total_advance += total_gold
		self.total_advance = total_advance
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
	def update_against(self):
		if self.total_idr_payment>0:
			#journal IDR nya aja
			account_list_idr=""
			for row in self.idr_payment:
				account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
				if account not in account_list_idr:
					if account_list_idr=="":
						account_list_idr=account
					else:
						account_list_idr="{},{}".format(account_list_idr,account)
			frappe.db.sql("""update `tabGL Entry` set against="{}" where voucher_no="{}" and account = "110.401.000 - Piutang Dagang - LMS" """.format(account_list_idr,self.name))
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi

		gl_entries = []
		gl = {}
		
		gl_piutang = []
		gl_piutang_idr = []
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = self.piutang_gold
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		#mapping allocated
		# inv_payment_map = {}
		# inv_tax_payment_map = {}
		# for row in self.invoice_table:
		# 	inv_payment_map[row.gold_invoice] = row.allocated
		# 	inv_tax_payment_map[row.gold_invoice] = row.tax_allocated
		# for row in self.customer_return:
		# 	inv_payment_map[row.invoice] = row.allocated

		nilai_selisih_kurs = 0
		#hitung selisih kurs untuk DP
		for row in self.gold_invoice_advance:
			nilai_selisih_kurs=nilai_selisih_kurs+(row.gold_allocated*(self.tutupan-row.tutupan))
		# distribute total gold perlu bagi per invoice
		#sisa= self.allocated_payment
		credit=0
		debit=0
		against_debit=""
		against_credit=""
		#untuk payment IDR
		account_list_idr=""
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
					if account_list_idr=="":
						account_list_idr=account
					else:
						account_list_idr="{},{}".format(account_list_idr,account)
				
		for row in self.invoice_table:
			if row.tax_allocated>0:
				gl_piutang_idr.append({
					"posting_date":self.posting_date,
					"account":piutang_idr,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":0,
					"credit":row.tax_allocated,
					"account_currency":"IDR",
					"debit_in_account_currency":0,
					"credit_in_account_currency":row.tax_allocated,
					#"against":"4110.000 - Penjualan - L",
					"against":account_list_idr,
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

			# if sisa>0 and row.allocated>0:
			if row.allocated>0:
				# payment=row.allocated
				# if sisa < row.allocated:
				# 	payment=sisa

				# inv_payment_map[row.gold_invoice]=inv_payment_map[row.gold_invoice]-payment
				gl_piutang.append({
					"posting_date":self.posting_date,
					"account":piutang_gold,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":0,
					"credit":row.allocated*row.tutupan,
					"account_currency":"GOLD",
					"debit_in_account_currency":0,
					"credit_in_account_currency":row.allocated,
					#"against":"4110.000 - Penjualan - L",
					"against":account_list_idr,
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
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*row.allocated)
		#frappe.msgprint("Invoice Payment credit = {} , debit = {}".format(credit,debit))
		for row in self.customer_return:
			#if sisa>0 and row.allocated>0:
			if row.allocated>0:
				# payment=row.allocated
				# if sisa<row.allocated:
				# 	payment = sisa
				# inv_payment_map[row.invoice]=inv_payment_map[row.invoice]-payment

				gl_piutang.append({
					"posting_date":self.posting_date,
					"account":piutang_gold,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":0,
					"credit":row.allocated*row.tutupan,
					"account_currency":"GOLD",
					"debit_in_account_currency":0,
					"credit_in_account_currency":row.allocated,
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
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*row.allocated)
					
		
		#adnvace GL
		adv=[]
		for row in self.invoice_advance:
			#advance_split=[]
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if row.idr_allocated>0:
				gl_piutang_idr.append({
					"posting_date":self.posting_date,
					"account":piutang_idr,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":row.idr_allocated,
					"credit":0,
					"account_currency":"IDR",
					"debit_in_account_currency":row.idr_allocated,
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
				})
			if deposit.idr_left >=row.idr_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left={} where name="{}" """.format(deposit.idr_left -row.idr_allocated,row.customer_deposit),as_list=1)
				#update GL for payment
				#if pembayaran di gunakan full
				if deposit.idr_left ==row.idr_allocated:
					frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Payment",against_voucher="{}" where voucher_no="{}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,row.customer_deposit,row.account_piutang),as_list=1)
				else:
				#if split needed
					frappe.db.sql("""update `tabGL Entry` set debit={0},debit_in_account_currency={0} where voucher_no="{1}" 
					and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{2}" and is_cancelled=0""".format(deposit.idr_left -row.idr_allocated,row.customer_deposit,row.account_piutang),as_list=1)
					adv.append({
									"posting_date":self.posting_date,
									"account":row.account_piutang,
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
			if row.gold_allocated>0:
				gl_piutang.append({
					"posting_date":self.posting_date,
					"account":piutang_gold,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":row.gold_allocated*row.tutupan,
					"credit":0,
					"account_currency":"GOLD",
					"debit_in_account_currency":row.gold_allocated,
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
				})
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
									"debit":row.gold_allocated*row.tutupan,
									"account_currency":"GOLD",
									"credit_in_account_currency":0,
									"debit_in_account_currency":row.gold_allocated,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Deposit",
									"against_voucher_type":"Gold Payment",
									"voucher_no":row.customer_deposit,
									#"against_voucher":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									})
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*row.gold_allocated)
		roundoff=0
#		frappe.msgprint("Customer Return credit = {} , debit = {}".format(credit,debit))
		for row in gl_piutang:
			roundoff=roundoff+row['debit']-row['credit']
			gl_entries.append(frappe._dict(row))
		for row in gl_piutang_idr:
			roundoff=roundoff+row['debit']-row['credit']
			gl_entries.append(frappe._dict(row))
		for row in gl_entries:
			if row.debit>0:
				against_credit="{} ,{}".format(against_credit,row.account)
			else:
				against_debit="{} ,{}".format(against_debit,row.account)
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
		# for row in adv:
		# 	roundoff=roundoff+row['debit']-row['credit']
		# 	gl_entries.append(frappe._dict(row))
		#	credit=credit+csk
		#	debit=debit+dsk
		#frappe.msgprint("Selisih Kurs credit = {} , debit = {}".format(credit,debit))
		for row in self.other_charges:
			if row.gold_amount>0:
				gl[row.category]=self.gl_dict(cost_center,row.account,row.gold_amount*self.tutupan,0,fiscal_years)
			else:
				gl[row.category]=self.gl_dict(cost_center,row.account,0,row.gold_amount*self.tutupan,fiscal_years)
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
			
		#	debit=debit+(self.discount_amount*self.tutupan)
		#	frappe.msgprint("Discount credit = {} , debit = {}".format(credit,debit))
		if self.write_off_total!=0 and 1==2:
			if self.write_off_total>0:
				# frappe.msgprint("+"+str(self.write_off_total))
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,self.write_off_total*-1,0,fiscal_years)
			else:
				# frappe.msgprint("-"+str(self.write_off_total*-1))
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,0,self.write_off_total,fiscal_years)

			# frappe.msgprint(str(gl[self.write_off_account]))
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
				gl[warehouse_account]=self.gl_dict(cost_center,warehouse_account,warehouse_value*self.tutupan,0,fiscal_years)
			if len(supplier_list)>0:
				uang_buat_beli_emas= frappe.db.get_single_value('Gold Selling Settings', 'uang_buat_beli_emas')
				for sup in supplier_list:
					gl[sup]=self.gl_dict_with_sup(cost_center,uang_buat_beli_emas,titip[sup],0,fiscal_years,sup)
		
		#roundoff=0
		
		for row in gl:
			# frappe.msgprint(str(row))
			roundoff=roundoff+gl[row]['debit']-gl[row]['credit']
			if gl[row]["debit"]>0:
				if gl[row]["account"] not in against_credit:
					against_credit="{} ,{}".format(against_credit,gl[row]["account"])
			else:
				if gl[row]["account"] not in against_debit:
					against_debit="{} ,{}".format(against_debit,gl[row]["account"])
		#add roundoff
		if roundoff!=0 :
			roundoff_coa= frappe.db.get_value('Company', self.company, 'round_off_account')
			if roundoff>0:
				gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,0,roundoff,fiscal_years)
				if roundoff_coa not in against_credit:
					against_debit = "{} ,{}".format(against_debit,roundoff_coa)
			else:
				gl[roundoff_coa]=gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,roundoff*-1,0,fiscal_years)
				if roundoff_coa not in against_credit:
					against_credit="{} ,{}".format(against_credit,roundoff_coa)
#			gl_entries.append(frappe._dict(gl[roundoff_coa]))
		for row in gl:
			if gl[row]["debit"]>0:
				gl[row]["against"]=against_debit
			else:
				gl[row]["against"]=against_credit
			
			if not gl[row]["account"]:
				frappe.msgprint(str(gl[row]))
				frappe.msgprint("test")
			gl_entries.append(frappe._dict(gl[row]))

		gl_entries = merge_similar_entries(gl_entries)

		# frappe.msgprint(str(gl_entries))
		return gl_entries
@frappe.whitelist(allow_guest=True)
def get_latest_transaction(customer):

	# cd_list = frappe.db.sql("""
	# SELECT * FROM `tabCustomer Deposit`
	# where customer = "{}" ORDER BY posting_date asc limit 3
	# """.format(customer),as_dict=True)
	# for row in cd_list:
	# 	baris_baru = {
	# 		'name': row.name,
	# 		'deposit_type' : row.deposit_type,
	# 		''
	# 	}
	return {"history":"Hello Word"}