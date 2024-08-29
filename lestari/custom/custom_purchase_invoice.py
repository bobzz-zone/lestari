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
def on_submit(doc, method=None):
    data_erp = doc.data_is_in_erp
    url = "http://192.168.3.25/api/Purchase-Invoice"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "octo@lms.com",
        ]

    if doc.owner in owner:
        if data_erp == 0:
            payment_term = ""
            due_date = doc.payment_schedule[0].due_date
            if doc.payment_schedule and doc.payment_schedule[0].payment_term:
                payment_term = doc.payment_schedule[0].payment_term
            else:
                payment_term = ""

            taxes = doc.taxes

            data = {
                "Owner": doc.owner,
                "invoice_erpnext": doc.name,
                "TransDate": doc.posting_date,
                "Amount": doc.grand_total,
                "Currency": doc.currency,
                "ExchangeRate": doc.conversion_rate,
                "Pajak": doc.pajak,
                "PPn": doc.ppn,
                "Supplier": doc.supplier,
                "Tujuan": doc.tujuan_doc,
                "DueDate": due_date,
                "PaymentTerm": payment_term,
                "NoNota": doc.bill_no,
                "PPnNo": doc.no_faktur,
                "items": []
            }
            for item in doc.items:
                if item.asset_category:
                    asset_category = item.asset_category
                else:
                    asset_category = ""

                if len(taxes) != 0:
                    if taxes[0].included_in_print_rate == 0:
                        qty = item.qty
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
                    "Description": item.description,
                    "Qty": item.qty,
                    "Price": rate,
                    "Total": amount,
                    "Unit": item.uom,
                    "Weight": item.weight_per_item,
                    "LinkPO": item.purchase_order,
                    "OrdPO": item.po_ordinal,
                    "asset_category": asset_category,
                }
                data['items'].append(baris_baru)

            try:
                # Membuat request POST
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
                frappe.db.set_value("Purchase Invoice", doc.name, "purchase_invoice_erp", respon['data']['ID'])
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

def on_update_after_submit(doc, method=None):
    data_erp = doc.data_is_in_erp
    url = "http://192.168.3.25/api/Purchase-Invoice"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "octo@lms.com",
        ]

    if doc.owner in owner:
        if data_erp == 0:
            data = {
                "purchase_invoice_erpnext": doc.name,
                "purchase_invoice_erp": doc.purchase_invoice_erp,
                "Tujuan": doc.tujuan_doc,
                "PPnNo": doc.no_faktur
            }

            try:
                # Membuat request POST
                response = requests.put(url, headers=headers, json=data)
                response.raise_for_status()

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

def on_cancel(doc, method=None):
    data_erp = doc.data_is_in_erp

    url = "http://192.168.3.25/api/Purchase-Invoice"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "octo@lms.com",
        ]

    if doc.owner in owner:
        if data_erp == 0:
            data = {
                "purchase_invoice_erpnext": doc.name,
                "purchase_invoice_erp": doc.purchase_invoice_erp,
                "Tujuan": doc.tujuan_doc
            }

            try:
                # Membuat request POST
                response = requests.delete(url, headers=headers, json=data)
                response.raise_for_status()

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

    