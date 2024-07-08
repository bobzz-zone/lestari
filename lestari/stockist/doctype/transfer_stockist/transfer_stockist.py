# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
from frappe.utils import getdate
from frappe.utils import now_datetime ,now
from frappe.utils import cint, flt

class TransferStockist(Document):
	@frappe.whitelist()
	def autoname(self):
		date = getdate(self.date)
		tahun = date.strftime("%y")
		bulan = date.strftime("%m")
		hari = date.strftime("%d")
		# frappe.throw(str(self.naming_series))
		self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
		self.name = self.naming_series.replace(".####", getseries(self.naming_series,4))
	def validate(self):
		# self.status = 'Draft'
		frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "{0}" where name = "{1}" """.format("Draft",self.name))
	def on_submit(self):
		print("-- Submitting Transfer Stockist "+self.name+" DONE --")
		ste = frappe.new_doc("Stock Entry")
		ste.stock_entry_transfer = "Transfer QC ke Stockist"
		ste.employee_id = self.pic
		ste.set_posting_time = 1
		ste.posting_date = self.date
		ste.remarks = self.keterangan
		ste.voucher_no = self.name
		ste.voucher_type = "Transfer Stockist"
		for row in self.items:
			doc = frappe.db.sql("""
                              SELECT item_code FROM `tabItem` WHERE kadar = "{}" and item_code LIKE "{}%" LIMIT 1
                              """.format(row.kadar,row.sub_kategori),as_dict=True)
			baris_baru = {
				'item_code' : doc[0].item_code,
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.t_warehouse,
				'qty' : row.qty_penambahan,
				'allow_zero_valuation_rate' : 1
			}
			ste.append("items",baris_baru)
		ste.flags.ignore_permissions = True
		ste.save()
		print("-- Submitting Stock Entry "+ste.name+" DONE --")
		print("-- DONE --")
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