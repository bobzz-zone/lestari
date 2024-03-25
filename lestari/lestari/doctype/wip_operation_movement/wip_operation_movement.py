# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WIPOperationMovement(Document):

	def validate(self):
		# # Check if operation is exists in WIP Operation
		operation_exists = frappe.db.exists('WIP Operation', {'operation': self.operation})
		if operation_exists:
			# 	# Get DocType WIP Operation by operation
			wip_operation = frappe.get_doc('WIP Operation', {'operation': self.operation})
		else:
			# 	# Insert WIP Operation
			wip_operation = frappe.new_doc('WIP Operation')
			wip_operation.operation = self.operation

		wip_operation.pcs = self.pcs if wip_operation.pcs is None else wip_operation.pcs + self.pcs
		wip_operation.weight = self.weight if wip_operation.weight is None else wip_operation.weight + self.weight
		wip_operation.flags.ignore_permissions = True
		wip_operation.save()
		# if self.type == 'IN':
		# 	wip_operation.pcs = self.pcs if wip_operation.pcs is None else wip_operation.pcs + self.pcs
		# 	wip_operation.weight = self.weight if wip_operation.weight is None else wip_operation.weight + self.weight
		# 	wip_operation.flags.ignore_permissions = True
		# 	wip_operation.save()
			
		# if self.type == 'OUT':
		# 	wip_operation.pcs = self.pcs if wip_operation.pcs is None else wip_operation.pcs - self.pcs
		# 	wip_operation.weight = self.weight if wip_operation.weight is None else wip_operation.weight - self.weight
		# 	wip_operation.flags.ignore_permissions = True
		# 	wip_operation.save()
