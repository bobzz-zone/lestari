# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now,today,add_days,flt
from datetime import datetime
import json

@frappe.whitelist()
def contoh_report(posting_date):
    piutang = []
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = [res.date(), today()]
    list_doc = frappe.db.sql("""
        SELECT
            a.name,
            a.customer,
            a.sales_bundle,
            a.posting_date,
            b.no_invoice,
            d.item,
            d.qty as bruto, 
            d.rate,
            d.amount as amount24k,
            e.mode_of_payment,
            e.amount as amountidr,
            f.customer_deposit as adv_gold,
            f.gold_deposit,
            f.gold_allocated,
            g.customer_deposit as adv_idr,
            g.idr_deposit,
            g.idr_allocated
        FROM
        `tabGold Payment` a
        JOIN
            (SELECT
            a.gold_invoice,
            a.parent AS pr,
            GROUP_CONCAT(a.gold_invoice SEPARATOR ",") no_invoice,
            b.name
            FROM
            `tabGold Payment Invoice` a
            JOIN `tabGold Payment` b
                ON a.parent = b.name
            GROUP BY b.`name`) b
            ON a.name = b.name
        LEFT JOIN `tabGold Payment Return` c
            ON a.name = c.parent
            AND c.allocated > 0
        LEFT JOIN `tabStock Payment` d
            ON a.name = d.parent
            AND d.amount > 0
        LEFT JOIN `tabIDR Payment` e
            ON a.name = e.parent
            AND e.amount > 0
        LEFT JOIN `tabGold Invoice Advance Gold` f
            ON a.name = f.parent
            AND f.gold_allocated > 0
        LEFT JOIN `tabGold Invoice Advance IDR` g
            ON a.name = g.parent
            AND g.idr_allocated > 0
        WHERE a.docstatus = 1 
        AND a.posting_date BETWEEN "{0}" AND "{1}" 
        ORDER BY a.`customer` ASC
    """.format(json_data[0],json_data[1]),as_dict = 1)
    # list_doc = frappe.db.get_list("Gold Payment", filters={'docstatus':1})
    # frappe.msgprint(str(list_doc))
    no = 0
    for row in list_doc:
        no+=1
        baris_baris = {
            'no' : no,
            'no_nota' : row.name,
            'posting_date' : row.posting_date,
            'customer' : row.customer,
            'item' : row.item,
            'bruto' : row.bruto,
            'rate' : row.rate,
            'amount24k' : row.amount24k,
            'mode_of_payment' : row.mode_of_payment,
            'amountidr' : row.amountidr,
            'adv_gold' : row.adv_gold,
            'gold_deposit' : row.gold_deposit,
            'gold_allocated' : row.gold_allocated,
            'adv_idr' : row.adv_idr,
            'idr_deposit' : row.idr_deposit,
            'idr_allocated' : row.idr_allocated,
            'no_invoice' : row.no_invoice,
            'sales_bundle' : row.sales_bundle,
        }
        # doc = frappe.get_doc("Gold Payment", row.name)
        # baris_baris = {
        #    'no': no,
        #    'no_nota': row.name,
        #    'customer': doc.customer,
        #    'sales_bundle': doc.sales_bundle,
        #    'posting_date' : doc.posting_date,
        #    'adv_gold': frappe.db.get_list("Gold Invoice Advance Gold", filters={'parent':row.name,'gold_allocated':['>',0]}, fields=['customer_deposit','gold_deposit','gold_allocated'], order_by='customer_deposit asc'),
        #    'total_adv_gold': doc.total_gold,
        #    'adv_idr': frappe.db.get_list("Gold Invoice Advance IDR", filters={'parent':row.name,'idr_allocated':['>',0]}, fields=['customer_deposit','idr_deposit','idr_allocated'], order_by='customer_deposit asc'),
        #    'total_adv_idr' : doc.total_idr_advance,
        #    'stock_payment' : frappe.db.get_list("Stock Payment", filters={'parent':row.name}, fields=['item','qty','rate','amount'], order_by='item asc'),
        #    'total_gold_payment' : doc.total_gold_payment,
        #    'total_bruto_discount' : doc.bruto_discount,
        #    'discount' : doc.discount,
        #    'discount_amount' : doc.discount_amount,
        #    'idr_payment' : frappe.db.get_list("IDR Payment", filters={'parent':row.name}, fields=['mode_of_payment','amount'], order_by='mode_of_payment asc'),
        #    'total_idr_payment' : doc.total_idr_payment,
        #    'tutupan': doc. tutupan,
        #    'write_off': doc.write_off,
        #    'inv': frappe.db.get_list("Gold Payment Invoice", filters={'parent':row.name}, fields=['gold_invoice','total','outstanding','outstanding_tax','allocated','total_bruto'], order_by='gold_invoice asc'),
        #    'total_invoice' : doc.total_invoice,
        #    'allocated_payment' : doc.allocated_payment,
        #    'total_pajak' : doc.total_pajak,
        #    'allocated_tax' : doc.allocated_idr_payment,
        #    'total_advance' : doc.total_advance,
        #    'jadi_deposit' : doc.jadi_deposit
        # }
        # adv_gold = frappe.db.get_list("Gold Invoice Advance Gold", filters={'parent':row.name}, fields=['customer_deposit','gold_deposit','gold_allocated'])
        piutang.append(baris_baris)
        # frappe.msgprint(str(piutang))
    # frappe.msgprint(str(piutang))  
    return piutang   