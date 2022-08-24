# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document

class GoldInvoice(Document):
	pass
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