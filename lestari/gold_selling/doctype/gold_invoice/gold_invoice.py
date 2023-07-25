import frappe
from frappe.utils import now_datetime ,now
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from frappe.utils import flt
class GoldInvoice(Document):
	def validate(self):

		if(self.no_invoice):
			self.name = self.no_invoice
			#total items
			total=0
			bruto=0
			for row in self.items:
				total=total+row.amount
				bruto=bruto+row.qty
			self.total=total
			self.total_bruto=bruto
			if not self.discount:
				self.discount=0
			self.grand_total=flt(self.total)-flt(self.discount)
			self.outstanding = self.grand_total - flt(self.total_advance)
			if self.outstanding<0:
				frappe.throw("Outstanding tidak boleh lebih kecil dari 0")
	@frappe.whitelist(allow_guest=True)
	def add_row_action(self):
		gi = frappe.db.sql("""select name,income_account from `tabGold Selling Item` where kadar="{}" and item_group="{}" """.format(self.kadar,self.category),as_list=1)
		if gi and len(gi)>0:
#			self.append("items",{"category":gi[0][0],"rate":get_gold_rate(gi[0][0],self.customer,self.customer_group)['nilai'],"kadar":self.kadar,"item_group":self.category,"income_account":gi[0][1],"qty":self.add_bruto})
			rate=flt(get_gold_rate(gi[0][0],self.customer,self.customer_group,self.subcustomer)['nilai'])
			print_rate=flt(get_gold_rate(gi[0][0],self.customer,self.customer_group,self.subcustomer)['nilai_print'])
			self.append("items",{"category":gi[0][0],"rate":rate,"kadar":self.kadar,"item_group":self.category,"income_account":gi[0][1],"qty":self.add_bruto,"amount":self.add_bruto*rate/100,"print_rate":print_rate,"print_amount":self.add_bruto*print_rate/100})
		else:
			frappe.msgprint("Product Not Found")
		self.kadar = ""
		self.category = ""
		self.add_bruto = ""
	def before_submit(self):
		if not self.posting_date:
			frappe.throw("Tanggal Invoice belum terisi")
		if self.outstanding<0:
			frappe.throw("Error, Outstanding should not be less than zero")
		if self.outstanding==0:
			self.invoice_status="Paid"
		else:
			self.invoice_status="Unpaid"

	def on_submit(self):
		if self.outstanding <= 0:
			frappe.throw(str(self.outstanding))
		else:
			self.make_gl_entries()
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		piutang_gold=self.piutang_gold
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#add GL untuk pph dan ppn
		if self.tax_status=="Tax":
			ppn_account = frappe.db.get_single_value('Gold Selling Settings', 'ppn_account')
			gl[ppn_account]={
				"posting_date":self.posting_date,
                                "account":ppn_account,
                                "party_type":"",
                                "party":"",
                                "cost_center":cost_center,
                                "debit":0,
                                "credit":self.ppn,
                                "account_currency":"IDR",
                                "debit_in_account_currency":0,
                                "credit_in_account_currency":self.ppn,
                                "voucher_type":"Gold Invoice",
                                "voucher_no":self.name,
                                "is_opening":"No",
                                "is_advance":"No",
                                "fiscal_year":fiscal_years,
                                "company":self.company,
                                "is_cancelled":0
			}
			if self.pph >0:
				pph_account = frappe.db.get_single_value('Gold Selling Settings', 'pph_account')
				gl[pph_account]={
					"posting_date":self.posting_date,
                                	"account":pph_account,
                                	"party_type":"",
                                	"party":"",
                                	"cost_center":cost_center,
                                	"debit":0,
                                	"credit":self.pph,
                                	"account_currency":"IDR",
                                	"debit_in_account_currency":0,
                                	"credit_in_account_currency":self.pph,
                                	"voucher_type":"Gold Invoice",
                                	"voucher_no":self.name,
                                	"is_opening":"No",
                                	"is_advance":"No",
                                	"fiscal_year":fiscal_years,
                                	"company":self.company,
                                	"is_cancelled":0
				}
			gl[piutang_idr]={
									"posting_date":self.posting_date,
									"account":piutang_idr,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":self.ppn+self.pph,
									"credit":0,
									"account_currency":"IDR",
									"debit_in_account_currency":self.ppn+self.pph,
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
		dsk=0
		csk=0
		#check selisihkurs
		#selisih kurs disabled =================karena g ada advance
		nilai_selisih_kurs=0
		# for row in self.gold_invoice_advance:
		# 	nilai_selisih_kurs=nilai_selisih_kurs+(row.gold_allocated*(self.tutupan-row.tutupan))
		#lebih dr 0 itu debit
		# if nilai_selisih_kurs!=0:
		# 	if nilai_selisih_kurs<0:
		# 		dsk=nilai_selisih_kurs*-1
		# 	else:
		# 		csk=nilai_selisih_kurs
		# 	gl[selisih_kurs]={
		# 							"posting_date":self.posting_date,
		# 							"account":selisih_kurs,
		# 							"party_type":"",
		# 							"party":"",
		# 							"cost_center":cost_center,
		# 							"debit":dsk,
		# 							"credit":csk,
		# 							"account_currency":"IDR",
		# 							"debit_in_account_currency":dsk,
		# 							"credit_in_account_currency":csk,
		# 							#"against":"4110.000 - Penjualan - L",
		# 							"voucher_type":"Gold Invoice",
		# 							"voucher_no":self.name,
		# 							#"remarks":"",
		# 							"is_opening":"No",
		# 							"is_advance":"No",
		# 							"fiscal_year":fiscal_years,
		# 							"company":self.company,
		# 							"is_cancelled":0
		# 							}
		#==============end of selisih kurs
		#1 untuk GL untuk piutang Gold
		gl[piutang_gold]={
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":(self.grand_total*self.tutupan)-dsk+csk,
									"credit":0,
									"account_currency":"GOLD",
									"debit_in_account_currency":self.grand_total,
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
		#2 untuk GL untuk penjualan IDR
		for row in self.items:
			if row.income_account in gl:
				gl[row.income_account]['credit']=gl[row.income_account]['credit']+(row.amount*self.tutupan)
				gl[row.income_account]['credit_in_account_currency']=gl[row.income_account]['credit']
			else:
				gl[row.income_account]={
									"posting_date":self.posting_date,
									"account":row.income_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":0,
									"credit":row.amount*self.tutupan,
									"account_currency":"IDR",
									"debit_in_account_currency":0,
									"credit_in_account_currency":row.amount*self.tutupan,
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
		#GL For Advance
		#===================di comment, perlu di check saat di re-open
		gl_entries=[]
		# if self.docstatus == 1:
		# 	adv=[]
		# 	for row in self.invoice_advance:
		# 		advance_split=[]
		# 		deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
		# 		if deposit.idr_left >=row.idr_allocated:
		# 			frappe.db.sql("""update `tabCustomer Deposit` set idr_left={} where name="{}" """.format(deposit.idr_left -row.idr_allocated,row.customer_deposit),as_list=1)
		# 			#update GL for payment
		# 			#if pembayaran di gunakan full
		# 			if deposit.idr_left ==row.idr_allocated:
		# 				frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Invoice",against_voucher="{}" where voucher_no="{}" 
		# 				and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,row.customer_deposit,piutang_idr),as_list=1)
		# 			else:
		# 			#if split needed
		# 				frappe.db.sql("""update `tabGL Entry` set debit={0},debit_in_account_currency={0} where voucher_no="{1}" 
		# 				and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{2}" and is_cancelled=0""".format(deposit.idr_left -row.idr_allocated,row.customer_deposit,piutang_idr),as_list=1)
		# 				adv.append({
		# 								"posting_date":self.posting_date,
		# 								"account":piutang_idr,
		# 								"party_type":"Customer",
		# 								"party":row.customer,
		# 								"cost_center":cost_center,
		# 								"credit":0,
		# 								"debit":row.idr_allocated,
		# 								"account_currency":"IDR",
		# 								"credit_in_account_currency":0,
		# 								"debit_in_account_currency":row.idr_allocated,
		# 								#"against":"4110.000 - Penjualan - L",
		# 								"voucher_type":"Customer Deposit",
		# 								"against_voucher_type":"Gold Invoice",
		# 								"voucher_no":row.customer_deposit,
		# 								"against_voucher":self.name,
		# 								#"remarks":"",
		# 								"is_opening":"No",
		# 								"is_advance":"No",
		# 								"fiscal_year":fiscal_years,
		# 								"company":self.company,
		# 								"is_cancelled":0
		# 								})
		# 	for row in self.gold_invoice_advance:
		# 		deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
		# 		if deposit.gold_left >=row.gold_allocated:
		# 			frappe.db.sql("""update `tabCustomer Deposit` set  gold_left={} where name="{}" """.format(deposit.gold_left -row.gold_allocated,row.customer_deposit),as_list=1)
		# 			#update GL for payment
		# 			#if pembayaran di gunakan full
		# 			if deposit.gold_left ==row.gold_allocated:
		# 				frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Gold Invoice",against_voucher="{}" where voucher_no="{}" 
		# 				and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format(self.name,row.customer_deposit,piutang_gold),as_list=1)
		# 			else:
		# 			#if split needed
		# 				frappe.db.sql("""update `tabGL Entry` set debit={},debit_in_account_currency={} where voucher_no="{}" 
		# 				and voucher_type="Customer Deposit" and against_voucher_type is NULL and against_voucher is NULL and account="{}" and is_cancelled=0""".format((deposit.gold_left -row.gold_allocated)*deposit.tutupan,deposit.gold_left -row.gold_allocated,row.customer_deposit,piutang_gold),as_list=1)
		# 				adv.append({
		# 								"posting_date":deposit.posting_date,
		# 								"account":piutang_gold,
		# 								"party_type":"Customer",
		# 								"party":row.customer,
		# 								"cost_center":cost_center,
		# 								"credit":0,
		# 								"debit":row.gold_allocated*deposit.tutupan,
		# 								"account_currency":"IDR",
		# 								"credit_in_account_currency":0,
		# 								"debit_in_account_currency":row.gold_allocated,
		# 								#"against":"4110.000 - Penjualan - L",
		# 								"voucher_type":"Customer Deposit",
		# 								"against_voucher_type":"Gold Invoice",
		# 								"voucher_no":row.customer_deposit,
		# 								"against_voucher":self.name,
		# 								#"remarks":"",
		# 								"is_opening":"No",
		# 								"is_advance":"No",
		# 								"fiscal_year":fiscal_years,
		# 								"company":self.company,
		# 								"is_cancelled":0
		# 								})
		# 	for row in adv:
		# 		gl_entries.append(frappe._dict(row))
		# elif self.docstatus==2:
		# 	frappe.db.sql("""update `tabGL Entry` set  against_voucher_type=NULL,against_voucher=NULL where against_voucher_type="Gold Invoice" and against_voucher="{}" """.format(self.name))
		# 	#merge if needed
		# 	gl_need_deleted=""
		# 	patch={}
		# 	for row in self.invoice_advance:
		# 		if row.gold_allocated>0:
		# 			gl_list=frappe.db.sql("""select name ,debit,credit,debit_in_account_currency,credit_in_account_currency from `tabGL Entry` where voucher_no="{}" and account="{}" and against_voucher_type=NULL and against_voucher=NULL and is_cancelled=0 """.format(row.customer_deposit,piutang_idr),as_list=1)
		# 			for det in gl_list:
		# 				if row.customer_deposit in patch:
		# 					if gl_need_deleted!="":
		# 						gl_need_deleted="""{},"{}" """.format(gl_need_deleted,det[0])
		# 					else:
		# 						gl_need_deleted=""" "{}" """.format(det[0])
		# 					patch[row.customer_deposit]['need_patch']=1
		# 					patch[row.customer_deposit]['debit']=flt(det[1])+patch[row.customer_deposit]['debit']
		# 					patch[row.customer_deposit]['credit']=flt(det[2])+patch[row.customer_deposit]['credit']
		# 					patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])+patch[row.customer_deposit]['debit_in_account_currency']
		# 					patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])+patch[row.customer_deposit]['credit_in_account_currency']
		# 				else:
		# 					patch[row.customer_deposit]={}
		# 					patch[row.customer_deposit]['need_patch']=0
		# 					patch[row.customer_deposit]['debit']=flt(det[1])
		# 					patch[row.customer_deposit]['name']=det[0]
		# 					patch[row.customer_deposit]['credit']=flt(det[2])
		# 					patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])
		# 					patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])
		# 	for row in self.gold_invoice_advance:
		# 		if row.gold_allocated>0:
		# 			gl_list=frappe.db.sql("""select name ,debit,credit,debit_in_account_currency,credit_in_account_currency from `tabGL Entry` where voucher_no="{}" and account="{}" and against_voucher_type=NULL and against_voucher=NULL and is_cancelled=0 """.format(row.customer_deposit,piutang_gold),as_list=1)
		# 			for det in gl_list:
		# 				if row.customer_deposit in patch:
		# 					if gl_need_deleted!="":
		# 						gl_need_deleted="""{},"{}" """.format(gl_need_deleted,det[0])
		# 					else:
		# 						gl_need_deleted=""" "{}" """.format(det[0])
		# 					patch[row.customer_deposit]['need_patch']=1
		# 					patch[row.customer_deposit]['debit']=flt(det[1])+patch[row.customer_deposit]['debit']
		# 					patch[row.customer_deposit]['credit']=flt(det[2])+patch[row.customer_deposit]['credit']
		# 					patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])+patch[row.customer_deposit]['debit_in_account_currency']
		# 					patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])+patch[row.customer_deposit]['credit_in_account_currency']
		# 				else:
		# 					patch[row.customer_deposit]={}
		# 					patch[row.customer_deposit]['need_patch']=0
		# 					patch[row.customer_deposit]['debit']=flt(det[1])
		# 					patch[row.customer_deposit]['name']=det[0]
		# 					patch[row.customer_deposit]['credit']=flt(det[2])
		# 					patch[row.customer_deposit]['debit_in_account_currency']=flt(det[3])
		# 					patch[row.customer_deposit]['credit_in_account_currency']=flt(det[4])
		# 	#delete merged GL
		# 	if gl_need_deleted!="":
		# 		frappe.db.sql("delete from `tabGL Entry` where name in ({})".format(gl_need_deleted),as_list=1)
		# 		#update value gl merged
		# 		for row in patch:
		# 			if patch[row]['need_patch']==1:
		# 				frappe.db.sql("""update `tabGL Entry` set debit={},credit={},debit_in_account_currency={},credit_in_account_currency={} where name="{}" """.format(patch[row]['debit'],patch[row]['credit'],patch[row]['debit_in_account_currency'],patch[row]['credit_in_account_currency'],patch[row]['name']),as_list=1)
		#==================end of line advance
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
	def on_cancel(self):
		self.flags.ignore_links=True
		#revert deposit balance
		for row in self.invoice_advance:
			if row.idr_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left + {} where name="{}" """.format(row.idr_allocated,row.customer_deposit),as_list=1)

		for row in self.gold_invoice_advance:
			if row.gold_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set  gold_left=gold_left + {} where name="{}" """.format(row.gold_allocated,row.customer_deposit),as_list=1)
		self.make_gl_entries()
	@frappe.whitelist(allow_guest=True)
	def get_gold_payment(self):
		doc = frappe.new_doc("Gold Payment")
		doc.customer = self.customer
		doc.warehouse = self.warehouse
		doc.posting_date = now()

		doc.total_invoice = self.outstanding
		baris_baru = {
			'gold_invoice':self.name,
			'total':self.outstanding,
			'due_date':self.due_date,
			'total':self.grand_total
		}
		doc.append("invoice_table",baris_baru)
		tutupan = frappe.db.sql("""
                        SELECT nilai
						FROM `tabGold Rates`
						WHERE nilai > 0
						AND DATE <= CURDATE() 
						ORDER BY DATE DESC
						LIMIT 1
                           """, as_dict=1)
		doc.tutupan = tutupan[0].nilai
		doc.flags.ignore_permissions = True
		doc.save()
		return doc

@frappe.whitelist(allow_guest=True)
def get_gold_rate(category,customer,customer_group,customer_print):
	#check if customer has special rates
	cr=0
	pr=0
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and category="{}" and valid_from<="{}" and type="Selling" and customer_type="Primary" """.format(customer,category,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		cr=customer_rate[0][0]
	customer_rate_print=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and category="{}" and valid_from<="{}" and type="Selling" and customer_type="Print Out" """.format(customer_print,category,now_datetime()),as_list=1)
	if customer_rate_print and customer_rate_print[0]:
		# return {"nilai_print":customer_rate_print[0][0]}
		pr=customer_rate_print[0][0]
	if cr==0:
		customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Rates` where customer_group="{}" and category="{}" and valid_from<="{}"  and type="Selling" """.format(customer_group,category,now_datetime()),as_list=1)
		if customer_group_rate and customer_group_rate[0]:
			# return {"nilai":customer_group_rate[0][0]}
			cr=customer_group_rate[0][0]
	return {"nilai":cr,"nilai_print":pr}

@frappe.whitelist(allow_guest=True)
def get_gold_purchase_rate(item,customer,customer_group):
	#check if customer has special rates
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and item="{}" and valid_from<="{}"  and type="Buying" order by valid_from desc """.format(customer,item,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		return {"nilai":customer_rate[0][0]}
	customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Rates` where customer_group="{}" and item="{}" and valid_from<="{}" and type="Buying"  order by valid_from desc """.format(customer_group,item,now_datetime()),as_list=1)
	if customer_group_rate and customer_group_rate[0]:
		return {"nilai":customer_group_rate[0][0]}
	return {"nilai":0}
