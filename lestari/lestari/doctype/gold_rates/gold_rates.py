# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class GoldRates(Document):
	pass
@frappe.whitelist():
def get_latest_rates():
	return frappe.db.sql("select nilai from `tabGold Rates` where date<=NOW() order by date desc",as_dict=True)[0]