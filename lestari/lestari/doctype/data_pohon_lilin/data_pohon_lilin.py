# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DataPohonLilin(Document):
    pass
    # def on_submit(self):
    #     make_proses_pohonan_lilin(self.name)

# @frappe.whitelist()
# def make_proses_pohonan_lilin(no_dpl):
#     sumber_doc = frappe.get_doc("Data Pohon Lilin", no_dpl)

#     target_doc = frappe.new_doc("Work Order Lilin")
#     # target_doc.employee_id = sumber_doc.created_by
#     target_doc.created_date = sumber_doc.created_date
#     target_doc.pohon_id = no_dpl
#     target_doc.set_sprue = sumber_doc.main_sprue
#     target_doc.warehouse_tujuan = "Lilin - L"

#     sumber_resep = frappe.db.sql("""
#     SELECT
#     dplr.no_spk,
#     dplr.resep_mul_karet,
#     dplr.mul_karet,
#     dplr.produk_id,
#     dplr.logo,
#     dplr.inject,
#     dplr.qty
#     FROM `tabData Pohon Lilin` dpl
#     JOIN `tabData Pohon Lilin Resep` dplr ON dplr.parent = dpl.name
#     WHERE dplr.parent = "{}"
#     """.format(no_dpl),as_dict=1)

#     kadar = []
#     for row in sumber_resep:
#         # qty = str(row.qty)
#         gambar = frappe.get_doc("Item", row.produk_id).image
#         kadar = frappe.get_doc("Item", row.produk_id).kadar
#         # html = "<img src='"+gambar+"' class='img-responsive' style='width:50%'/>"
#         inject = row.qty / row.inject
#         # frappe.msgprint(html)
#         baris_baru = {
#                 "no_spk": row.no_spk,
#                 "resep_mul_karet": row.resep_mul_karet,
#                 "mul_karet": row.mul_karet,
#                 "produk_id": row.produk_id,
#                 "image": gambar,
#                 "logo": row.logo,
#                 "inject": inject,
#                 "qty" : row.qty,
#                 # "gambar": html
#                 }

#         target_doc.append("tabel_pohon",baris_baru)

#         frappe.msgprint(str(kadar))
#         target_doc.kadar = kadar

#     # sumber_batu = frappe.db.sql("""
#     # SELECT DISTINCT
#     # item.item_code,
#     # (rilb.qty * dplr.qty) AS total
#     # FROM `tabItem` item
#     # JOIN `tabResep Investment Lilin Batu` rilb ON rilb.batu = item.item_code
#     # JOIN `tabResep Mul Karet` rmk ON rmk.name = rilb.parent
#     # JOIN `tabData Pohon Lilin Resep` dplr ON dplr.resep_cetakan = rmk.name
#     # WHERE dplr.parent = "{}"
#     # ORDER BY item.item_code DESC
#     # """.format(no_dpl),as_dict=1)
#     sumber_batu = frappe.db.sql("""
#     SELECT DISTINCT
#     item.item_code,
#     rmk.rubber_mould as mul_karet,
#     rmk.name as resep_mul_karet,
#     rilb.qty as qty,
#     (rilb.qty * dplr.qty) AS total
#     FROM `tabItem` item
#     JOIN `tabResep Investment Lilin Batu` rilb ON rilb.batu = item.item_code
#     JOIN `tabResep Mul Karet` rmk ON rmk.name = rilb.parent
#     JOIN `tabData Pohon Lilin Resep` dplr ON dplr.resep_mul_karet = rmk.name
#     WHERE dplr.parent = "{}"
#     ORDER BY item.item_code DESC
#     """.format(no_dpl),as_dict=1)

#     temp = []
#     total = 0
#     material = ""
#     for row in sumber_batu:
#         if len(temp) < 1:
#             temp.append({
#                 "mul_karet": row['mul_karet'],
#                 "resep_mul_karet" : row['resep_mul_karet'],
#                 "item_code" : row['item_code'],
#                 "qty" : row['qty'],
#                 "total": row['total']
#             })
#         else:
#             for check in temp:
#                 if check['item_code'] == row['item_code']:
#                     check['total'] = check['total'] + row['total']
#                 else:
#                     status = True
#                     for check_2 in temp:
#                         if check_2['item_code'] == row['item_code']:
#                             status = False
#                     if status:
#                         temp.append({
#                             "mul_karet": row['mul_karet'],
#                             "resep_mul_karet" : row['resep_mul_karet'],
#                             "item_code" : row['item_code'],
#                             "qty" : row['qty'],
#                             "total": row['total']
#                         })
                       
#     for row in sumber_batu:
#         # frappe.msgprint(str(row))
#         baris_baru = {
#         "mul_karet": row['mul_karet'],
#         "resep_mul_karet" : row['resep_mul_karet'],
#         "batu" : row['item_code'],
#         "qty" : row['qty'],
#         "total_qty": row['total']
#         } 
#         target_doc.append("tabel_batu",baris_baru)

#     target_doc.flags.ignore_permissions = True
#     target_doc.save()    
#     # return target_doc.as_dict()