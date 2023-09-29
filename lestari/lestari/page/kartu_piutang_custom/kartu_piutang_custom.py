# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

@frappe.whitelist()
def contoh_report():
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
            WHERE docstatus = 1
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
            WHERE docstatus = 1
    """,as_dict = 1)
    no = 0
    for row in list_doc:
        no+=1
        baris_baris = {
            'no' : no,
            'voucher_no' : row.voucher_no,
            'voucher_type' : row.voucher_type,
            'date' : frappe.format(row.posting_date,{'fieldtype':'Date'}),
            'customer' : row.customer,
            'tutupan' : flt(row.tutupan),
            'outstanding' : flt(row.outstanding),
            'deposit_gold' : flt(row.deposit_emas),
            'deposit_idr': flt(row.deposit_idr),
        }
        piutang.append(baris_baris)
    frappe.msgprint(str(piutang))  
    return piutang   