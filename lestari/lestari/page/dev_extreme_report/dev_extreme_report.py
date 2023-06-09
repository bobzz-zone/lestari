# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def contoh_report():
    po = []
    list_doc = frappe.get_list("Purchase Order")
    no = 0
    for row in list_doc:
        no+=1
        doc = frappe.get_doc("Purchase Order", row)
        baris_baris = {
            'no' : no,
            'name' : doc.name,
            'transaction_date' : frappe.format(doc.transaction_date,{'fieldtype':'Date'}),
            'schedule_date' : frappe.format(doc.schedule_date,{'fieldtype':'Date'}),
            'pajak' : doc.pajak,
            'ppn' : doc.ppn,
            'no_faktur' : doc.no_faktur,
            'supplier' : doc.supplier,
            'total_qty' : doc.total_qty,
            'currency' : doc.currency,
            # 'total' : frappe.utils.fmt_money(doc.total,currency=frappe.db.get_value("Currency",doc.currency,"Symbol")),
            'total' : doc.total,
            'status' : doc.status
        }
        po.append(baris_baris)
    # frappe.msgprint(str(po))  
    return po  