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
    # frappe.throw(str(doc.posting_date))
    posting_date = str(doc.posting_date)
    
    url = "http://192.168.3.25/api/Purchase-Receive"

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    is_return = doc.is_return

    owner = [
        "aditya@lms.com",
        "yonatan@lms.com",
        "novandre@lms.com",
        "EviPuji@lms.com"
        ]

    if doc.owner in owner and doc.modified_by != "izzi@lms.com":
        taxes = doc.taxes

        # if is_return == 0:
        #     id_purchase_receive_erp == ""
        # else:
        #     id_purchase_receive_erp = doc.id_purchase_receive_erp

        data = {
            "id_purchasereceive_erpnext": doc.name,
            "tujuan": doc.tujuan_doc,
            "Owner": doc.owner,
            "supplier": doc.supplier,
            "TransDate": posting_date,
            "no_sj": doc.supplier_delivery_note,
            "PPn": doc.ppn,
            "items": []
        }
        for item in doc.items:
            qty = item.qty

            if len(taxes) != 0:
                if taxes[0].included_in_print_rate == 0:
                    tax_amount = taxes[0].tax_amount
                    ppn_amount = tax_amount / qty
                    rate = item.net_rate + ppn_amount
                else:
                    tax_amount = 0
                    ppn_amount = 0
                    rate = item.net_rate
            else:
                tax_amount = 0
                ppn_amount = 0
                rate = item.net_rate

            baris_baru = {
                "material_request_erpnext": item.material_request,
                "mr_ordinal": item.ordinal,
                "qty": item.qty,
                "item_code": item.item_code,
                "description": item.description,
                "price": rate,
                "purchase_order": item.purchase_order,
                "po_ordinal": item.po_ordinal,
                "weight": item.total_weight
            }

            data['items'].append(baris_baru)
    
        try:
            if is_return == 0:
                # Membuat request POST
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()

                frappe.db.set_value("Purchase Receipt", doc.name, "id_purchase_receive_erp", respon['data']['ID'])
                frappe.db.commit()
            else:
                # Membuat request PUT
                response = requests.put(url, headers=headers, json=data)
                response.raise_for_status()  # Raises an HTTPError for bad responses

                respon = response.json()

                frappe.db.set_value("Purchase Receipt", doc.name, "id_purchase_receive_cancelled", respon['data']['ID'])
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
    url = "http://192.168.3.25/api/Purchase-Receive"

    posting_date = str(doc.posting_date)

    # Data perlu dikirim dalam format JSON
    headers = {
        "Content-Type": "application/json",
    }

    owner = [
        "aditya@lms.com",
        "yonatan@lms.com"
        ]

    if doc.modified_by != "izzi@lms.com":
        frappe.throw("BTB Tidak Bisa Dibatalkan")
        return
        
    # if doc.owner in owner and doc.modified_by != "izzi@lms.com":

    #     data = {
    #         "id_purchasereceive_erpnext": doc.name,
    #         "tujuan": doc.tujuan_doc,
    #         "Owner": doc.owner,
    #         "supplier": doc.supplier,
    #         "TransDate": posting_date,
    #         "id_purchase_receive_erp": doc.id_purchase_receive_erp,
    #         "no_sj": doc.supplier_delivery_note,
    #         "items": []
    #     }
    #     for item in doc.items:
    #         baris_baru = {
    #             "material_request_erpnext": item.material_request,
    #             "mr_ordinal": item.ordinal,
    #             "qty": item.qty,
    #             "item_code": item.item_code,
    #             "price": item.net_rate
    #         }

    #         data['items'].append(baris_baru)

    #     try:
    #         # Membuat request POST
    #         response = requests.put(url, headers=headers, json=data)
    #         response.raise_for_status()  # Raises an HTTPError for bad responses

    #         respon = response.json()

    #         frappe.db.set_value("Purchase Receipt", doc.name, "id_purchase_receive_cancelled", respon['data']['ID'])
    #         frappe.db.commit()
    #     except requests.exceptions.HTTPError as http_err:
    #         frappe.msgprint(f"HTTP error occurred: {http_err}")
    #         frappe.throw(f"Response text: {response.text}")
    #     except requests.exceptions.ConnectionError as conn_err:
    #         frappe.throw(f"Connection error occurred: {conn_err}")
    #     except requests.exceptions.Timeout as timeout_err:
    #         frappe.throw(f"Timeout error occurred: {timeout_err}")
    #     except requests.exceptions.RequestException as req_err:
    #         frappe.throw(f"An error occurred: {req_err}")
    #     except Exception as e:
    #         frappe.throw(f"An unexpected error occurred: {e}")
