# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class KonfirmasiPaymentReturn(Document):
    def on_submit(self):
        pass
        # ste = frappe.new_doc("Stock Entry")
        # ste.
    @frappe.whitelist()
    def get_serah_terima(self):
        doc = frappe.get_doc("Serah Terima Payment Stock", self.serah_terima)
        for row in doc.details:
            if frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']) == "Rongsok":
                if row.sudah_cek == 0:
                    rongsok = {
						'item': row.item,
						'qty': row.qty,
						'voucher_type': row.voucher_type,
						'voucher_no': row.voucher_no
					}
                    self.append("detail_rongsok",rongsok)
            if frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']) == "Perhiasan":
                if row.sudah_cek == 0:
                    perhiasan = {
						'item': row.item,
						'qty': row.qty,
						'voucher_type': row.voucher_type,
						'voucher_no': row.voucher_no
					}
                    self.append("detail_perhiasan",perhiasan)
