# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import requests
import json
import datetime
import erpnext
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from math import ceil
from frappe import _
from frappe.utils import add_days, cint, flt, nowdate
from erpnext.controllers.status_updater import StatusUpdater

class PurchaseRequest(StatusUpdater):
	def __init__(self, *args, **kwargs):
		super(PurchaseRequest, self).__init__(*args, **kwargs)
		self.status_updater = [
			{
				"source_dt": "Purchase Request Item", 
				"target_dt": "Material Request Item",
				"join_field": "child_id",
				"target_field": "request_qty",
				"target_parent_dt": "Material Request",
				"target_parent_field": "per_requested",
				"target_ref_field": "qty",
				"source_field": "qty",
				"percent_join_field": "material_request",
				# "overflow_type": "requested",
			}
		]

	@frappe.whitelist()
	def get_mr_pending(self):
		self.items = []
		condition = ""
		if self.search_by_id_mr:
			condition += " AND a.idmaterial_request = '{0}'".format(self.search_by_id_mr)
		if self.filter_by_proses:
			condition += " AND b.proses = '{0}'".format(self.filter_by_proses)

		# Default ordering
		condition2 = "a.idmaterial_request DESC, b.ordinal ASC"

		# Only apply additional sorting if any of the sort parameters are set
		if any([self.sort, self.sort_by_id_mr, self.sort_by_proses]):
			condition2 = ""
			if self.sort:
				condition2 += "a.transaction_date {0}".format(self.sort)
			if self.sort_by_id_mr:
				condition2 += ", a.idmaterial_request {0}".format(self.sort_by_id_mr) if condition2 else "a.idmaterial_request {0}".format(self.sort_by_id_mr)
			if self.sort_by_proses:
				condition2 += ", b.proses {0}".format(self.sort_by_proses) if condition2 else "b.proses {0}".format(self.sort_by_proses)
			condition2 += ", b.ordinal ASC"

		list_mr_pending = frappe.db.sql("""
		SELECT
			a.name as mr_name,
			a.idmaterial_request as idmr,
			a.schedule_date as s_date,
			a.transaction_date as t_date,
			b.*
		FROM
			`tabMaterial Request` a
		JOIN `tabMaterial Request Item` b
			ON a.name = b.parent 
			AND b.`ordered_qty` != b.qty 
			AND b.request_qty != b.qty
		WHERE a.material_request_type = "Purchase"
		AND a.docstatus = 1
		AND a.status IN ("Pending", "Partially ordered", "Partially requested")
		AND a.transaction_date > "2023-12-31"
		{0}
		ORDER BY {1}""".format(condition, condition2), as_dict=True, debug=True)
		# frappe.msgprint(str(list_mr_pending))
		meta = frappe.get_meta("Purchase Request Item").get("fields")
		for row in list_mr_pending:
			target_d = frappe.new_doc("Purchase Request Item", parent_doc=self, parentfield="items")
			for df in meta:
				val = row.get(df.fieldname)
				target_d.set(df.fieldname, val)
			target_d.update(
				{
					"idmaterial_request": row.idmr,
					"material_request": row.mr_name,
					"child_id": row.name,
					"ordinal_mr": row.ordinal,
					"transaction_date": row.t_date,
					"schedule_date": row.s_date
				}
			)
			self.append("items", target_d)

	@frappe.whitelist()
	def create_po(self):
		try:
			items = []
			transaction_date = ""
			for row in self.items:
				transaction_date = row.transaction_date
				baris_baru = {
					"item_code": row.item_code,
					"product_original": "Isikan nama Produk Dari Supplier",
					"qty": row.qty,
					"uom": row.uom,
					"rate": row.rate,
					"schedule_date": row.schedule_date,
					"amount": row.amount,
					"description": row.description
				}
				items.append(baris_baru)
			frappe.msgprint(str(baris_baru))
			# Buat item baru
			po = frappe.get_doc({
				'doctype': 'Purchase Order',
				'transaction_date': transaction_date,
				'supplier': self.supplier,
				'tujuan_doc': self.tujuan_doc,
				'items': items
			})

			po.insert()
			frappe.db.commit()
			print(f"Purchase Order telah dibuat dengan nomor {po.name}")
			return po
		except Exception as e:
			return ("Gagal buat Purchase Order:", str(e))

	def on_cancel(self):
		self.update_prevdoc_status()

	def on_submit(self):
		self.update_prevdoc_status()
		for row in self.items:
			request_qty = frappe.db.get_value("Material Request Item", row.child_id, "request_qty")
			frappe.db.set_value("Purchase Request Item", row.child_id, "request_qty", request_qty)
		frappe.db.commit()

		url = "http://192.168.3.25/api/Purchase-Request"

		# Data perlu dikirim dalam format JSON
		headers = {
			"Content-Type": "application/json",
		}

		owner = [
			"izzi@lms.com",
			]

		# if self.owner in owner:
		if self.data_is_in_erp == 0:
			data = {
				"Owner": self.owner,
				"TransDate": self.transaction_date,
				"Employee": self.employee_erp,
				"pr_erpnext": self.name,
				"items": []
			}
			for item in self.items:
				baris_baru = {
					"idmaterial_request": item.idmaterial_request,
					"ordinal_mr": item.ordinal_mr,
					"qty": item.qty,
					"unit": item.uom
				}
				data['items'].append(baris_baru)

			try:
				# Membuat request POST
				response = requests.post(url, headers=headers, json=data)
				response.raise_for_status()  # Raises an HTTPError for bad responses

				respon = response.json()
				frappe.db.set_value("Purchase Request", self.name, "purchase_request_erp", respon['data']['ID'])
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