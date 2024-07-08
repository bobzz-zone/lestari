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

def submit():
    # URL endpoint untuk Material Request
    doc = frappe.get_doc("Material Request", "MRI24070824")
    url = "http://192.168.3.25/api/Material-Request"
    if doc.from_laravel == 0:
        # Data yang akan dikirimkan dalam request POST
        data = {
        "UserName": doc.nickname,
        "Owner": doc.owner,
        "Remarks": doc.name,
        "TransDate": doc.transaction_date.strftime("%Y-%m-%d"),
        "Department": doc.id_deparment,
        "Employee": doc.employee_erp,
        "Type": doc.material_request_type,
        "Jenis": doc.jenis_dokumen,
        "Docstatus": doc.docstatus,
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
            baris_baru = {
                "Product": item.idproduct,
                "ProductNote": deskripsi_non_stock,
                "ProductNonStock": item.item_code,
                "Qty": item.qty,
                "Unit": item.uom,
                "Proses": Proses,
                "Note": item.keterangan,
                "RequiredDate": item.schedule_date.strftime("%Y-%m-%d")
            }
            data['items'].append(baris_baru)

        print(data)

        # Data perlu dikirim dalam format JSON
        headers = {
            "Content-Type": "application/json",
        }

        # Membuat request POST
        response = requests.post(url, headers=headers, json=data)

        # Memeriksa status response
        if response.status_code == 200:
            print("Material Request berhasil dibuat")
            print(response.json())
        else:
            print("Gagal membuat Material Request")
            print(response.status_code)
            print(response.text)
        