# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now,today,add_days,flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(posting_date = None):
    invoice = []
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = [res.date(), today()]
    list_doc = frappe.db.sql("""
        SELECT
           *
        FROM
        `tabGold Invoice`
        WHERE docstatus = 1
        AND posting_date BETWEEN "{0}" AND "{1}"
        ORDER BY posting_date ASC
    """.format(json_data[0],json_data[1]),as_dict = 1)
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