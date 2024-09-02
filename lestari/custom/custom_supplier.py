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
    # update_po_percentage(doc, method)
    url = "http://192.168.3.25/api/Supplier-Other"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "alyaa@lms.com",
        "octo@lms.com"
        ]

    # if doc.owner == "izzi@lms.com":
    if doc.owner in owner and doc.modified_by != "izzi@lms.com":
        # if doc.address_line1:
        #     address_line1 = doc.address_line1
        # else:
        address_line1 = ""

        data = {
            "Owner": doc.owner,
            "kode_supplier": doc.kode_supplier,
            "supplier_name": doc.supplier_name,
            "phone": doc.phone,
            "mobile_no": doc.mobile_no,
            "email_id": doc.email_id,
            "primary_address": address_line1
        }

        try:
            # Membuat request POST
            response = requests.post(url, headers=headers, json=data)
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