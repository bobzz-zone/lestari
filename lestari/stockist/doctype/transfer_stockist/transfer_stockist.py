# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import cint, flt


class TransferStockist(Document):
	def validate(self):
		# self.status = 'Draft'
		frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "{0}" where name = "{1}" """.format("Draft",self.name))
	def on_submit(self):
		# self.status = 'Submitted'
		frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "{0}" where name = "{1}" """.format("Submitted",self.name))
	def on_cancel(self):
		frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "{0}" where name = "{1}" """.format("Cancelled",self.name))
		# self.status = 'Cancelled'

@frappe.whitelist()
def buat_baru(source_name, target_doc=None):
	def postprocess(source, target):
		target.transfer = source.transfer
		

	doclist = get_mapped_doc(
		"Transfer Stockist",
		source_name,
		{
			"Transfer Stockist": {
				"doctype": "Transfer Stockist",
				"field_map": {
					"transfer": "transfer",
				},
				"validation": {"docstatus": ["=", 1]},
			},
		},
		target_doc,
		postprocess,
	)

	return doclist