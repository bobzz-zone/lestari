# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now,today,add_days,flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(posting_date = None):
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = [res.date(), today()]
    # frappe.msgprint(str(res.date()))
    piutang = []
    list_doc = frappe.db.sql("""
            SELECT
            customer,
            no_invoice,
            "0" AS deposit_emas,
            "0" AS deposit_idr,
            tutupan,
            outstanding,
            posting_date,
            "Gold Invoice" AS voucher_type,
            NAME AS voucher_no
            FROM
            `tabGold Invoice`
            WHERE docstatus = 1 and outstanding > 0
            AND posting_date BETWEEN "{0}" AND "{1}"
            UNION
            SELECT
            customer,
            "0" AS no_invoice,
            gold_left AS deposit_emas,
            idr_left AS deposit_idr,
            tutupan,
            "0" AS outstanding,
            posting_date,
            "Customer Deposit" AS voucher_type,
            NAME AS voucher_no
            FROM
            `tabCustomer Deposit`
            WHERE docstatus = 1 and ( gold_left > 0  or idr_left > 0 )
            AND posting_date BETWEEN "{0}" AND "{1}"
    """.format(json_data[0],json_data[1]),as_dict = 1)
    no = 0
    url = "http://erpnext.lestarigold.co.id/app"
    for row in list_doc:
        doctype = row.voucher_type.lower().replace(' ', '-')
        no+=1
        baris_baris = {
            'no' : no,
            'voucher_no' : row.voucher_no,
            'voucher_type' : row.voucher_type,
            'posting_date' : row.posting_date,
            'customer' : row.customer,
            'tutupan' : flt(row.tutupan),
            'outstanding' : flt(row.outstanding),
            'deposit_gold' : flt(row.deposit_emas),
            'deposit_idr': flt(row.deposit_idr),
        }
        piutang.append(baris_baris)
    # frappe.msgprint(str(piutang))  
    return piutang   