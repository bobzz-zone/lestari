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

def after_insert(doc, method):
    url = "http://192.168.3.25/api/Transfer-Material"

    LinkID = ""
    LinkOrd = ""

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "izzi@lms.com",
        "yonatan@lms.com",
        "kharies@lms.com",
        "IkaM@lms.com",
        "EndangS@lms.com",
        "gustig@lms.com",
        "frita@lms.com",
        ]
    if doc.owner in owner:
        if doc.creation == doc.modified:
            data = {
                "creation": doc.creation,
                "modified": doc.modified,
                "employee_erp": doc.employee_id,
                "docstatus":doc.docstatus,
                "Status": "Create",
                "nameStockEntry": doc.name,
                "Department":doc.id_department,
                "Owner": doc.owner,
                "TransDate": doc.posting_date,
                "Type": doc.stock_entry_type,
                "item": []
            }
            for item in doc.items:
                if item.material_request:
                    LinkID = item.material_request
                    LinkOrd = item.ordinal
                baris_baru = {
                    "Product": item.item_code,
                    "Qty": item.qty,
                    "Note": item.keterangan,
                    "LinkID": LinkID,
                    "LinkOrd": LinkOrd,
                    "Proses": item.id_proses
                }
                data['item'].append(baris_baru)
            
            try:
                # Membuat request POST
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
                frappe.db.set_value("Stock Entry", doc.name, "id_transfer_erp", respon['data'][0]['ID'])
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
            
def on_update(doc, method):
    url = "http://192.168.3.25/api/Transfer-Material"

    LinkID = ""
    LinkOrd = ""

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "izzi@lms.com",
        "yonatan@lms.com",
        "kharies@lms.com",
        "IkaM@lms.com",
        "EndangS@lms.com",
        "gustig@lms.com",
        "frita@lms.com",
        ]
    if doc.owner in owner:
        if doc.creation != doc.modified and doc.docstatus == 0:
            data = {
                "creation": doc.creation,
                "modified": doc.modified,
                "employee_erp": doc.employee_id,
                "docstatus":doc.docstatus,
                "Status": "Update",
                "nameStockEntry": doc.name,
                "Department":doc.id_department,
                "Owner": doc.owner,
                "TransDate": doc.posting_date,
                "Type": doc.stock_entry_type,
                "id_transfer_erp": doc.id_transfer_erp,
                "item": []
            }
            for item in doc.items:
                if item.material_request:
                    LinkID = item.material_request
                    LinkOrd = item.ordinal
                baris_baru = {
                    "Product": item.item_code,
                    "Qty": item.qty,
                    "Note": item.keterangan,
                    "LinkID": LinkID,
                    "LinkOrd": LinkOrd,
                    "Proses": item.id_proses
                }
                data['item'].append(baris_baru)
            
            try:
                # Membuat request POST
                response = requests.put(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
                frappe.db.set_value("Stock Entry", doc.name, "id_transfer_erp", respon['data'][0]['ID'])
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
    
def on_change(doc, method):
    # return
    url = "http://192.168.3.25/api/Transfer-Material"

    LinkID = ""
    LinkOrd = ""

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "izzi@lms.com"
        ]
    if doc.owner != "arikba@lms.com":
        if doc.docstatus == 1 and doc.workflow_state=="Posted":
            # if doc.id_transfer_erp:
            data = {
                "creation": doc.creation,
                "modified": doc.modified,
                "modified_by": doc.modified_by,
                "employee_erp": doc.employee_id,
                "docstatus":doc.docstatus,
                "Status": "Submit",
                "nameStockEntry": doc.name,
                "Department":doc.id_department,
                "Owner": doc.owner,
                "TransDate": doc.posting_date,
                "Type": doc.stock_entry_type,
                "id_transfer_erp": doc.id_transfer_erp,
                "posting_status": doc.workflow_state,
                "item": []
            }
            for item in doc.items:
                baris_baru = {
                    "Product": item.item_code,
                    "Qty": item.qty,
                    "Note": item.keterangan,
                    "LinkID": item.material_request,
                    "LinkOrd": item.ordinal,
                    "Proses": item.id_proses
                }
                data['item'].append(baris_baru)


            try:
                # Membuat request POST
                response = requests.put(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()
                frappe.db.set_value("Stock Entry", doc.name, "id_transfer_erp", respon['data'][0]['ID'])
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
                return
                # frappe.msgprint(f"An unexpected error occurred: {e}")