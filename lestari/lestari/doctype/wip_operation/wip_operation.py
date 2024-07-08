# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WIPOperation(Document):
	@frappe.whitelist()
	def reset_wip(self):
		query = frappe.db.sql("""
		SELECT
			SUM(A.weight) as weight,
			SUM(A.pcs) AS pcs
			FROM
			(
			SELECT
			ROUND(SUM(A.weight),2) AS weight,
			SUM(A.pcs) AS pcs
			FROM
			`tabWIP Operation Movement` A 
			WHERE
			A.operation = '{0}'
			AND DATE(A.creation) = DATE(NOW())
			AND A.type = 'IN'

			UNION

			SELECT
			ROUND(SUM(A.weight),2) AS weight,
			SUM(A.pcs) AS pcs
			FROM
			`tabWIP Operation Movement` A 
			WHERE
			A.operation = '{0}'
			AND DATE(A.creation) = DATE(NOW())
			AND A.type = 'OUT'
			) A
		""".format(self.operation),as_dict=1)
		frappe.msgprint(str(query))
		self.weight = query[0].weight
		self.pcs = query[0].pcs
		self.flags.ignore_permissions = True
		self.save()
