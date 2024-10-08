# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now, today, add_days, flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(from_date=None, to_date=None, used=None):
    # start_date, end_date = get_date_range(posting_date)
    start_date, end_date = [from_date,to_date]
    query = build_query(start_date, end_date, used)
    list_doc = frappe.db.sql(query, as_dict=1)
    return process_results(list_doc)

def get_date_range(posting_date):
    if posting_date:
        return json.loads(posting_date)
    else:
        return [datetime.today().replace(day=1).strftime('%Y-%m-%d'), today()]

def build_query(start_date, end_date, used):
    gold_invoice_query = """
    SELECT
        customer,
        no_invoice,
        bundle,
        0 AS total_deposit_emas,
        0 AS deposit_emas,
        0 AS total_other_charges_gold,
        0 AS total_deposit_idr,
        0 AS deposit_idr,
        tutupan,
        grand_total,
        outstanding,
        0 AS total_cpr,
        0 AS cpr,
        posting_date,
        'Gold Invoice' AS voucher_type,
        NAME AS voucher_no,
        NAME AS no_nota
    FROM
        `tabGold Invoice`
    WHERE docstatus = 1
        AND posting_date BETWEEN "{0}" AND "{1}"
    """
    
    if used == 1:
        gold_invoice_query += " AND outstanding > 0"
    
    customer_deposit_query = """
    SELECT
        customer,
        no_nota AS no_invoice,
        sales_bundle AS bundle,
        total_gold_deposit AS total_deposit_emas,
        gold_left AS deposit_emas,
        total_other_charges_gold,
        total_idr_deposit AS total_deposit_idr,
        idr_left AS deposit_idr,
        tutupan,
        0 AS grand_total,
        0 AS outstanding,
        0 AS total_cpr,
        0 AS cpr,
        posting_date,
        'Customer Deposit' AS voucher_type,
        NAME AS voucher_no,
        no_nota
    FROM
        `tabCustomer Deposit`
    WHERE docstatus = 1
        AND posting_date BETWEEN "{0}" AND "{1}"
    """
    
    if used == 1:
        customer_deposit_query += " AND (gold_left > 0 OR idr_left > 0)"
    
    customer_payment_return_query = """
    SELECT
        customer,
        no_nota AS no_invoice,
        sales_bundle AS bundle,
        0 AS total_deposit_emas,
        0 AS deposit_emas,
        0 AS total_other_charges_gold,
        0 AS total_deposit_idr,
        0 AS deposit_idr,
        tutupan,
        0 AS grand_total,
        0 AS outstanding,
        total AS total_cpr,
        outstanding AS cpr,
        posting_date,
        'Customer Payment Return' AS voucher_type,
        NAME AS voucher_no,
        no_nota
    FROM
        `tabCustomer Payment Return`
    WHERE docstatus = 1
        AND posting_date BETWEEN "{0}" AND "{1}"
    """
    
    if used == 1:
        customer_payment_return_query += " AND outstanding > 0"
    
    return f"""
    {gold_invoice_query}
    UNION
    {customer_deposit_query}
    UNION
    {customer_payment_return_query}
    """.format(start_date, end_date)

def process_results(list_doc):
    piutang = []
    for index, row in enumerate(list_doc, start=1):
        baris_baris = {
            'no': index,
            'voucher_no': row.voucher_no,
            'voucher_type': row.voucher_type,
            'no_nota': row.no_nota,
            'bundle': row.bundle,
            'posting_date': row.posting_date,
            'customer': row.customer,
            'tutupan': flt(row.tutupan),
            'total_invoice': flt(row.grand_total),
            'outstanding': flt(row.outstanding),
            'total_deposit_gold': flt(row.total_deposit_emas) + flt(row.total_other_charges_gold),
            'deposit_gold': flt(row.deposit_emas),
            'total_deposit_idr': flt(row.total_deposit_idr),
            'deposit_idr': flt(row.deposit_idr),
            'total_cpr': flt(row.total_cpr),
            'cpr': flt(row.cpr),
            'summarize': flt(row.outstanding) + flt(row.cpr) - flt(row.deposit_emas)
        }
        piutang.append(baris_baris)
    return piutang