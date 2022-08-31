import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
class GoldInvoice(Document):
	def validate(self):
		#total items
		total=0
		for row in self.items:
			total=total+row.amount
		self.total=total
		if not self.discount:
			self.discount=0
		self.grand_total=self.total-self.discount
	def on_submit(self):
		if self.outstanding<=0:
			frappe.throw("Error, Outstanding should not be less than zero")
		for row in self.invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.idr_left >=row.idr_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left={} where name="{}" """.format(deposit.idr_left -row.idr_allocated,row.customer_deposit),as_list=1)
		for row in self.gold_invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.gold_left >=row.gold_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set  gold_left={} where name="{}" """.format(deposit.gold_left -row.gold_allocated,row.customer_deposit),as_list=1)
		self.make_gl_entries()
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl_entries={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		gl_entries[piutang_gold]=frappe._dict({
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":self.grand_total*self.tutupan,
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
									})
		#2 untuk GL untuk penjualan IDR
		for row in self.items:
			if row.income_account in gl_entries:
				gl_entries[row.income_account]['credit']=gl_entries[row.income_account]['credit']+(row.amount*self.tutupan)
				gl_entries[row.income_account]['credit_in_account_currency']=gl_entries[row.income_account]['credit']
			else:
				gl_entries[row.income_account]=frappe._dict({
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
									})
		#GL For Advance
		nilai_selisih_kurs=0
		for row in self.gold_invoice_advance:
			nilai_selisih_kurs=nilai_selisih_kurs+(row.gold_allocated*(self.tutupan-row.tutupan))
		#lebih dr 0 itu debit
		if nilai_selisih_kurs!=0:
			dsk=0
			csk=0
			if nilai_selisih_kurs>0:
				dsk=nilai_selisih_kurs
			else:
				csk=nilai_selisih_kurs
			gl_entries[selisih_kurs]=frappe._dict({
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
									"voucher_type":"Gold Invoice",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									})
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
				piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 and cint(self.update_stock) and cint(auto_accounting_for_stock):
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
	def on_cancel(self):
		#revert deposit balance
		for row in self.invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.idr_left >=row.idr_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left=idr_left + {} where name="{}" """.format(row.idr_allocated,row.customer_deposit),as_list=1)
		for row in self.gold_invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.gold_left >=row.gold_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set  gold_left=gold_left + {} where name="{}" """.format(row.gold_allocated,row.customer_deposit),as_list=1)

	def get_gl_dict(self, args, account_currency=None, item=None):
		"""this method populates the common properties of a gl entry record"""

		posting_date = args.get("posting_date") or self.get("posting_date")
		fiscal_years = get_fiscal_years(posting_date, company=self.company)
		if len(fiscal_years) > 1:
			frappe.throw(
				_("Multiple fiscal years exist for the date {0}. Please set company in Fiscal Year").format(
					formatdate(posting_date)
				)
			)
		else:
			fiscal_year = fiscal_years[0][0]

		gl_dict = frappe._dict(
			{
				"company": self.company,
				"posting_date": posting_date,
				"fiscal_year": fiscal_year,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"remarks": self.get("remarks") or self.get("remark"),
				"debit": 0,
				"credit": 0,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": 0,
				"is_opening": self.get("is_opening") or "No",
				"party_type": None,
				"party": None,
				"project": self.get("project"),
				"post_net_value": args.get("post_net_value"),
			}
		)

		accounting_dimensions = get_accounting_dimensions()
		dimension_dict = frappe._dict()

		for dimension in accounting_dimensions:
			dimension_dict[dimension] = self.get(dimension)
			if item and item.get(dimension):
				dimension_dict[dimension] = item.get(dimension)

		gl_dict.update(dimension_dict)
		gl_dict.update(args)

		if not account_currency:
			account_currency = get_account_currency(gl_dict.account)

		if gl_dict.account and self.doctype not in [
			"Journal Entry",
			"Period Closing Voucher",
			"Payment Entry",
			"Purchase Receipt",
			"Purchase Invoice",
			"Stock Entry",
		]:
			self.validate_account_currency(gl_dict.account, account_currency)

		if gl_dict.account and self.doctype not in [
			"Journal Entry",
			"Period Closing Voucher",
			"Payment Entry",
		]:
			set_balance_in_account_currency(
				gl_dict, account_currency, self.get("conversion_rate"), self.company_currency
			)

		return gl_dict
@frappe.whitelist(allow_guest=True)
def get_gold_rate(category,customer,customer_group):
	#check if customer has special rates
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Selling Rates` where customer="{}" and category="{}" and valid_from<="{}"  """.format(customer,category,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		return {"nilai":customer_rate[0][0]}
	customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Selling Rates` where customer_group="{}" and category="{}" and valid_from<="{}"  """.format(customer_group,category,now_datetime()),as_list=1)
	if customer_group_rate and customer_group_rate[0]:
		return {"nilai":customer_group_rate[0][0]}
	return {"nilai":0}

#needupdate
@frappe.whitelist(allow_guest=True)
def get_gold_purchase_rate(item_group,customer,customer_group):
	#check if customer has special rates
	customer_rate=frappe.db.sql("""select nilai_beli from `tabCustomer Rates` where customer="{}" and item_group="{}" and valid_from<="{}"  """.format(customer,item_group,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		return {"nilai":customer_rate[0][0]}
	customer_group_rate=frappe.db.sql("""select nilai_beli from `tabCustomer Group Rates` where customer_group="{}" and item_group="{}" and valid_from<="{}"  """.format(customer_group,item_group,now_datetime()),as_list=1)
	if customer_group_rate and customer_group_rate[0]:
		return {"nilai":customer_group_rate[0][0]}
	return {"nilai":0}