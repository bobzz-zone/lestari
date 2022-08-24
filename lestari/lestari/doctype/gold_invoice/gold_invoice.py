# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document

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
		for row in self.invoice_advance:
			deposit=frappe.get_doc("Customer Deposit",row.customer_deposit)
			if deposit.idr_left >=row.idr_allocated and deposit.gold_left >=row.gold_allocated:
				frappe.db.sql("""update `tabCustomer Deposit` set idr_left={} , gold_left={} where name="{}" """.format(deposit.idr_left -row.idr_allocated ,deposit.gold_left -row.gold_allocated,row.customer_deposit),as_list=1)
@frappe.whitelist(allow_guest=True)
def get_gold_rate(item_group,customer,customer_group):
	#check if customer has special rates
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and item_group="{}" and valid_from<="{}"  """.format(customer,item_group,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		return {"nilai":customer_rate[0][0]}
	customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Rates` where customer_group="{}" and item_group="{}" and valid_from<="{}"  """.format(customer_group,item_group,now_datetime()),as_list=1)
	if customer_group_rate and customer_group_rate[0]:
		return {"nilai":customer_group_rate[0][0]}
	return {"nilai":0}
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