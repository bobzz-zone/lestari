# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockReturnTransfer(Document):
	@frappe.whitelist()
	def get_kpr(self):
		doc = frappe.get_doc("Konfirmasi Payment Return",self.no_doc)
		for row in doc.detail_perhiasan:
			perhiasan = {
				'item': row.item,
				'berat': row.tolak_qty,
				'voucher_type': row.voucher_type,
				'voucher_no': row.voucher_no,
				'child_type':row.doctype,
				'child_name':row.name,
			}
			self.append("transfer_details",perhiasan)
		for row in doc.detail_rongsok:
			rongsok = {
				'item': row.item,
				'berat': row.tolak_qty,
				'voucher_type': row.voucher_type,
				'voucher_no': row.voucher_no,
				'child_type':row.doctype,
				'child_name':row.name,
			}
			self.append("transfer_details",rongsok)
	def on_submit(self):
		for row in self.transfer_details:
			if row.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',1)
				