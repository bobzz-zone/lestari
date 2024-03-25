# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime

class WorklogTesting(Document):

	def insertWIPOperationMovement(self,operation:str, employee:str, spko:str, weight:float, pcs:int, type:str):
		newWIPOperationMovement = frappe.new_doc('WIP Operation Movement')
		newWIPOperationMovement.operation = operation
		newWIPOperationMovement.employee = employee
		# Create current date
		current_date = datetime.datetime.now()
		newWIPOperationMovement.transdate = current_date.strftime("%Y-%m-%d")
		newWIPOperationMovement.spko = spko
		newWIPOperationMovement.work_log = self.name
		newWIPOperationMovement.weight = weight
		newWIPOperationMovement.pcs = pcs
		newWIPOperationMovement.type = type
		newWIPOperationMovement.flags.ignore_permissions = True
		newWIPOperationMovement.save()

	def on_submit(self):
		totalWeight = 0
		totalPcs = self.total_pcs
		for row in self.list_spko:
			# frappe.db.sql("""UPDATE `tabSPKO` SET status = 'Done' WHERE name = '{}' """.format(row.spko))

			# set spko work log
			frappe.db.set_value('SPKO', {'name': row.spko}, 'work_log', self.name)
			# set spko status
			frappe.db.set_value('SPKO', {'name': row.spko}, 'status', 'Done')
			totalWeight += float(frappe.db.get_value('SPKO', {'name': row.spko}, 'berat'))
			# frappe.db.commit()

		
		# Get Workstation from current operation
		workstation = frappe.db.get_value('Operation', {'name': self.operation}, 'workstation')
		# list workstation for available stock WIP Operation
		availableWorkstation = ['Poles'] 
		if workstation in availableWorkstation:
			# get next operation from Operation
			nextOperation = frappe.db.get_value('Operation', {'name': self.operation}, 'next_operation')
			for spko in self.list_spko:
				weight = float(frappe.db.get_value('SPKO', {'name': spko.spko}, 'berat'))
				pcs = int(frappe.db.get_value('SPKO', {'name': spko.spko}, 'jumlah_pcs'))

				self.insertWIPOperationMovement(self.operation, self.employee, spko.spko, weight*-1, pcs*-1, 'OUT')
				if nextOperation != 'Transfer Material':
					self.insertWIPOperationMovement(nextOperation, self.employee, spko.spko, weight, pcs, 'IN')

		
		


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
