# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormOrder(Document):
	@frappe.whitelist()
	def match_data(self):
		#sort all item into grouped array of category
		data={}
		#for row in self.items:
		#	if 
