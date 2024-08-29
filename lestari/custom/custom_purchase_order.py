# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import requests
import datetime
import json
import erpnext
import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, nowdate
from frappe.model.mapper import get_mapped_doc
from math import ceil

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None, args=None):
    def update_item(obj, target, source_parent):
        # frappe.msgprint(str(obj.as_dict()))
        qty = (
            flt(flt(obj.stock_qty) - flt(obj.request_qty)) / target.conversion_factor
            if flt(obj.stock_qty) > flt(obj.request_qty)
            else 0
        )
        target.qty = qty
        target.ordinal = obj.ordinal

    def validasi_item(doc):
        if not (args and args.get("filtered_children")):
            return flt(doc.request_qty, doc.precision("request_qty")) < flt(doc.stock_qty, doc.precision("request_qty"))
        return doc.name in args.get("filtered_children")

    doclist = get_mapped_doc(
        "Purchase Request",
        source_name,
        {
            "Purchase Request": {
            "doctype": "Purchase Order",
            "validation": {
                "docstatus": ["=", 1],
            },
            "field_no_map": [
                "data_is_in_erp"
            ],
        },
        "Purchase Request Item": {
            "doctype": "Purchase Order Item",
            "field_map": {
                "child_id": "material_request_item",
                "material_request": "material_request",
            },
            "postprocess": update_item,
            "condition": validasi_item,
        },
    },
        target_doc,
    )

    return doclist

@frappe.whitelist()
def calculate_po_percentage(purchase_request):
    pr_doc = frappe.get_doc("Purchase Request", purchase_request)
    
    total_pr_qty = 0
    total_po_qty = 0
    
    # Membuat dictionary untuk menyimpan qty per item dari PR
    pr_items = {item.item_code: item.qty for item in pr_doc.items}
    
    # Menghitung total qty dari PR
    for item in pr_doc.items:
        total_pr_qty += item.qty
    
    # Mengambil semua PO yang terkait dengan PR ini
    pos = frappe.get_all("Purchase Order", 
                         filters={"purchase_request": purchase_request, "docstatus": 1},
                         fields=["name"])
    
    for po in pos:
        po_doc = frappe.get_doc("Purchase Order", po.name)
        for item in po_doc.items:
            if item.item_code in pr_items:
                ordered_qty = min(item.qty, pr_items[item.item_code])
                total_po_qty += ordered_qty
    
    # Menghitung persentase
    if total_pr_qty > 0:
        percentage = (total_po_qty / total_pr_qty) * 100
    else:
        percentage = 0
    
    return {
        "percentage": round(percentage, 2),
        "total_pr_qty": total_pr_qty,
        "total_po_qty": total_po_qty
    }

@frappe.whitelist()
def update_pr_percentage(purchase_request):
    result = calculate_po_percentage(purchase_request)
    pr_doc = frappe.get_doc("Purchase Request", purchase_request)
    pr_doc.po_percentage = result["percentage"]
    pr_doc.save()
    pr_doc.add_comment("Comment", f"PO Percentage updated: {result['percentage']}%")

# Fungsi untuk dijalankan saat PO di-submit atau di-cancel
def update_po_percentage(doc, method):
    if doc.purchase_request:
        update_pr_percentage(doc.purchase_request)

@frappe.whitelist()
def on_submit(doc, method=None):
    # update_po_percentage(doc, method)
    url = "http://192.168.3.25/api/Purchase-Order"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "alyaa@lms.com",
        "octo@lms.com"
        ]
    data_erp = doc.data_is_in_erp

    if doc.owner in owner and doc.modified_by != "izzi@lms.com":
        if data_erp == 0:
            payment_term = ""
            transaction_date = doc.transaction_date
            due_date = doc.payment_schedule[0].due_date
            if doc.payment_schedule and doc.payment_schedule[0].payment_term:
                payment_term = doc.payment_schedule[0].payment_term
            else:
                payment_term = ""

            taxes = doc.taxes

            # transaction_date=transaction_date.strftime("%Y-%m-%d")
            data = {
                "Owner": doc.owner,
                "erpnext_id": doc.name,
                "Remarks": doc.note,
                "Tujuan": doc.tujuan_doc,
                "TransDate": transaction_date,
                "Supplier": doc.supplier,
                "Amount": doc.grand_total,
                "Currency": doc.currency,
                "ExchangeRate": doc.conversion_rate,
                "Pajak": doc.pajak,
                "PPn": doc.ppn,
                "due_date": due_date,
                "payment_term": payment_term,
                "items": []
            }

            for item in doc.items:
                qty = item.qty

                if len(taxes) != 0:
                    if taxes[0].included_in_print_rate == 0:
                        tax_amount = taxes[0].tax_amount
                        ppn_amount = tax_amount / qty
                        rate = item.rate + ppn_amount
                        amount = item.amount + tax_amount
                    else:
                        tax_amount = 0
                        ppn_amount = 0
                        rate = item.rate
                        amount = item.amount
                else:
                    tax_amount = 0
                    ppn_amount = 0
                    rate = item.rate
                    amount = item.amount
                
                baris_baru = {
                    "Product": item.item_code,
                    "ProductNote": item.description,
                    "ProductOriginal": item.product_original,
                    "Qty": item.qty,
                    "Unit": item.uom,
                    "Price":rate,
                    "Discount": 0,
                    "ItemValue": rate,
                    "Total": amount,
                    "purchase_request": item.purchase_request,
                    "pr_ordinal": item.pr_ordinal
                }
                data['items'].append(baris_baru)

            try:
                # Membuat request POST
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
                frappe.db.set_value("Purchase Order", doc.name, "id_purchase_order_erp", respon['data']['ID'])
                frappe.db.set_value("Purchase Order", doc.name, "po_no", respon['data']['SW'])
                frappe.db.commit()
            except requests.exceptions.HTTPError as http_err:
                frappe.msgprint(f"HTTP error occurred: {http_err}")
                frappe.throw(f"Response text: {response.text}")
            except requests.exceptions.ConnectionError as conn_err:
                frappe.throw(f"Connection error occurred: {conn_err}")
            except requests.exceptions.Timeout as timeout_err:
                frappe.throw(f"Timeout error occurred: {timeout_err}")
            except requests.exceptions.RequestException as req_err:
                frappe.throw(f"An error occurred: {req_err}")
            except Exception as e:
                frappe.throw(f"An unexpected error occurred: {e}")

def on_cancel(doc, method=None):
    # update_po_percentage(doc, method)
    url = "http://192.168.3.25/api/Purchase-Order"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "alyaa@lms.com",
        "octo@lms.com"
        ]
    data_erp = doc.data_is_in_erp

    if doc.owner in owner and doc.modified_by != "izzi@lms.com":
        if data_erp == 0:
            data = {
                "id_purchase_order_erp": doc.id_purchase_order_erp,
                "id_purchase_order_erpnext": doc.name,
                "cancel_by": doc.modified_by,
            }

            try:
                # Membuat request POST
                response = requests.put(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
            except requests.exceptions.HTTPError as http_err:
                frappe.msgprint(f"HTTP error occurred: {http_err}")
                frappe.throw(f"Response text: {response.text}")
            except requests.exceptions.ConnectionError as conn_err:
                frappe.throw(f"Connection error occurred: {conn_err}")
            except requests.exceptions.Timeout as timeout_err:
                frappe.throw(f"Timeout error occurred: {timeout_err}")
            except requests.exceptions.RequestException as req_err:
                frappe.throw(f"An error occurred: {req_err}")
            except Exception as e:
                frappe.throw(f"An unexpected error occurred: {e}")
