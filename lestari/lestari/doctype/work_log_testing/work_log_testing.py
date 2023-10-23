# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WorklogTesting(Document):
	def on_submit(self):
		for row in self.list_spko:
			frappe.db.sql("""UPDATE `tabSPKO` SET status = 'Done' WHERE name = '{}' """.format(row.spko))
			# frappe.db.commit()

# @frappe.whitelist()
# def getAllTransactions():
# 	data = {
# 		"message": "helloWorld",
# 		"data": [
# 			"adjwdoajda",
# 			"dawldjka"
# 		]
# 	}
# 	return data
