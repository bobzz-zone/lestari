# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockReturnTransfer(Document):
	@frappe.whitelist()
	def get_kpr(self):
		list_kpr = frappe.db.get_list("Konfirmasi Payment Return",filters={'sales':self.sales})
		for row in list_kpr:
			frappe.msgprint(str(row))
			doc = frappe.get_doc("Konfirmasi Payment Return", row)
			for col in doc.detail_perhiasan:
				customer = frappe.db.get_value(col.parenttype,col.parent,'customer')
				subcustomer = frappe.db.get_value(col.parenttype,col.parent,'subcustomer')
				perhiasan = {
					'item': col.item,
					'berat': col.tolak_qty,
					'customer': customer,
					'sub_costomer'
     				'kadar',
					'voucher_type': col.voucher_type,
					'voucher_no': col.voucher_no,
					'child_type':col.doctype,
					'child_name':col.name,
				}
				self.append("transfer_details",perhiasan)
			for col in doc.detail_rongsok:
				rongsok = {
					'item': col.item,
					'berat': col.tolak_qty,
					'voucher_type': col.voucher_type,
					'voucher_no': col.voucher_no,
					'child_type':col.doctype,
					'child_name':col.name,
				}
				self.append("transfer_details",rongsok)
	def on_submit(self):
		for row in self.transfer_details:
			if row.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',1)
				