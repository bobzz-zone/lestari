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
def after_insert(doc, method=None):
    data_erp = doc.data_is_in_erp
    url = "http://192.168.3.25/api/Payment-Entry"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        # "octo@lms.com",
        # "alyaa@lms.com",
        "atikro@lms.com",
        "aldona@lms.com"
        ]

    if doc.owner == "izzi@lms.com":
        if data_erp == 0 and doc.mode_of_payment != "Kas Bon Sementara":  # Kas Bon Sementara (Pembelian dari supir / Tunai)

            for i in doc.references:
                if i.reference_doctype != "Purchase Invoice":
                    frappe.throw("Gagal Create Payment Entry. Purchase Invoice Tidak Ditemukan")

            if doc.deductions:
                difference_amount = doc.deductions[0].amount
            else:
                difference_amount = 0

            data = {
                "owner": doc.owner,
                "mode_of_payment": doc.mode_of_payment,
                "PaymentEntry_erpnext": doc.name,
                "TransDate": doc.posting_date,
                "supplier": doc.party_name,
                "paid_amount": doc.paid_amount,
                "difference_amount": difference_amount,
                "paid_from": doc.paid_from,
                "references": []
            }
            for item in doc.references:
                    
                baris_baru = {
                    "reference_name": item.reference_name,
                    "allocated_amount": item.allocated_amount
                }
                data['references'].append(baris_baru)

            try:
                # Membuat request POST
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()

                # Update DB
                frappe.db.set_value("Payment Entry", doc.name, "id_payment_entry_erp", respon['data']['ID'])
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