# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

@frappe.whitelist()
def contoh_report():
    invoice = []
    list_doc = frappe.db.sql("""
        SELECT
           *
        FROM
        `tabGold Invoice`
        WHERE docstatus = 1
        ORDER BY posting_date ASC
    """,as_dict=1)
    no = 0
    for row in list_doc:
        no+=1
        baris_baris = {
            'no' : no,
            'customer' : row.customer,
            'subcustomer' : row.subcustomer,
            'no_nota' : row.name,
            'posting_date' : row.posting_date,
            'sales' : row.sales_partner,
            'bundle' : row.bundle,
            'berat_kotor' : row.total_bruto,
            'berat_bersih': row.total,
            'satuan' : row.type_emas,
            'tutupan' : row.tutupan,
            'tax_status' : row.tax_status,
            'ppn' : row.ppn,
            'pph' : row.pph,
            'user' : row.owner
        }
        invoice.append(baris_baris)
        # frappe.msgprint(str(baris_baris))
    return invoice   