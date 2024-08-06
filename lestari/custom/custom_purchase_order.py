# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
import requests
import json
from math import ceil

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, nowdate
import datetime

import erpnext


@frappe.whitelist()
def on_submit(doc, method=None):
    url = "http://192.168.3.25/api/Purchase-Order"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "izzi@lms.com",
        ]
    if doc.owner in owner:
        transaction_date = doc.transaction_date
        # transaction_date=transaction_date.strftime("%Y-%m-%d")
        data = {
            "Owner": doc.owner,
            "erpnext_id": doc.name,
            "Remarks": doc.note,
            "Tujuan": doc.tujuan_doc,
            "TransDate": transaction_date,
            "Supplier": doc.supplier,
            "Amount": doc.total,
            "Currency": doc.currency,
            "ExchangeRate": doc.conversion_rate,
            "Pajak": doc.pajak,
            "items": []
        }
        for item in doc.items:
            baris_baru = {
                "Product": item.item_code,
                "ProductNote": item.description,
                "ProductOriginal": item.product_original,
                "Qty": item.qty,
                "Unit": item.uom,
                "Price":item.rate,
                "Discount": 0,
                "ItemValue": item.rate,
                "Total": item.amount,
                "material_request": item.material_request,
                "ordinal_mr": item.ordinal
            }
            data['items'].append(baris_baru)

        try:
            # Membuat request POST
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            respon = response.json()
            frappe.db.set_value("Purchase Order", doc.name, "id_purchase_order_erp", respon['data']['ID'])
            frappe.db.commit()
        except requests.exceptions.HTTPError as http_err:
            frappe.msgprint(f"HTTP error occurred: {http_err}")
            frappe.msgprint(f"Response text: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            frappe.msgprint(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            frappe.msgprint(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            frappe.msgprint(f"An error occurred: {req_err}")
        except Exception as e:
            frappe.msgprint(f"An unexpected error occurred: {e}")