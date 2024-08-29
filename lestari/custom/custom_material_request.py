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

def submit(doc, method):
    # URL endpoint untuk Material Request
    # frappe.msgprint(str(doc.name))
    # frappe.msgprint(str(doc.from_laravel))
    # frappe.msgprint(str(method))
    # doc = frappe.get_doc("Material Request", docname)
    # print("Start kirim data")
    url = "http://192.168.3.25/api/Material-Request"
    if doc.from_laravel == "0":
        # Data yang akan dikirimkan dalam request POST
        # frappe.msgprint("Material Request Submitting...")
        transaction_date = doc.transaction_date
        if frappe.session.user =="Administrator":
            transaction_date=transaction_date.strftime("%Y-%m-%d")
        # frappe.msgprint(transaction_date)
        data = {
        "UserName": doc.nickname,
        "Owner": doc.owner,
        "Remarks": doc.name,
        "TransDate": transaction_date,
        "Department": doc.id_deparment,
        "Employee": doc.employee_erp,
        "Type": doc.material_request_type,
        "Jenis": doc.jenis_dokumen,
        "Docstatus": doc.docstatus,
        "jenis_mr": doc.jenis_mr,
        "items": []
        }
        for item in doc.items:
            if item.proses:
                if item.id_proses:
                    Proses = item.id_proses
                else:
                    Proses = 0
            else:
                Proses = 0
            deskripsi_non_stock = item.deskripsi_non_stock.replace('\"', '\\\"') if item.deskripsi_non_stock else ""
            schedule_date = item.schedule_date
            if frappe.session.user =="Administrator":
                schedule_date = schedule_date.strftime("%Y-%m-%d")
            baris_baru = {
                "Product": item.idproduct,
                "ProductNote": deskripsi_non_stock,
                "ProductNonStock": item.item_code,
                "Qty": item.qty,
                "Unit": item.uom,
                "Proses": Proses,
                "Note": item.keterangan,
                "RequiredDate": schedule_date
            }
            data['items'].append(baris_baru)

        # print(data)

        # Data perlu dikirim dalam format JSON
        headers = {
            "Content-Type": "application/json",
        }

        # Membuat request POST
        response = requests.post(url, headers=headers, json=data)

        # Memeriksa status response
        if response.status_code == 200:
            # frappe.msgprint("Material Request berhasil dibuat")
            respon = response.json()
            # frappe.msgprint(str(respon['data']))
            frappe.db.set_value("Material Request", doc.name, "idmaterial_request", respon['data'][0]['ID'])
            frappe.db.commit()

        else:
            frappe.msgprint("Gagal membuat Material Request")
            frappe.msgprint(str(response.status_code))
            frappe.throw(str(response.text))
    else:
        # frappe.msgprint("Data ini sudah di submit dari ERPLaravel")
        print("Data ini sudah di submit dari ERPLaravel")
        
