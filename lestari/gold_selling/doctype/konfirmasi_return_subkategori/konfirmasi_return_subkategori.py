# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class KonfirmasiReturnSubkategori(Document):
	@frappe.whitelist()
	def get_konfirmasi(self):
		doc = frappe.get_doc("Konfirmasi Payment Return", self.no_konfirmasi)
		if doc.detail_perhiasan:
			for row in doc.detail_perhiasan:
				if row.is_out == 0 and row.is_confirm == 0:
					baris_baru = {
						'idx_konfirmasi': row.idx,
						'item': row.item,
						# 'sub_kategori': frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']),
						'terima_berat': row.terima_qty,
						'berat_pembayaran': row.qty,
						'customer':row.customer,
						'voucher_type':row.voucher_type,
						'voucher_no':row.voucher_no,
						'child_table':row.doctype,
						'child_id':row.name
					}
				self.append("items",baris_baru)
		if doc.detail_rongsok:
			for row in doc.detail_rongsok:
				if row.is_out == 0 and row.is_confirm == 0:
					baris_baru = {
						'idx_konfirmasi': row.idx,
						'item': row.item,
      					# 'sub_kategori': frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']),
						'terima_berat': row.terima_qty,
						'berat_pembayaran': row.qty,
						'customer':row.customer,
						'voucher_type':row.voucher_type,
						'voucher_no':row.voucher_no,
						'child_table':row.doctype,
						'child_id':row.name
					}
				self.append("items",baris_baru)