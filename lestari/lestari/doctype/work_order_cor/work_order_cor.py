# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import timedelta
from frappe.utils import flt, add_days, nowdate


class WorkOrderCor(Document):
	def validate(self):
		target_doc = frappe.new_doc("Material Request")
		target_doc.material_request_type = "Material Transfer"
		target_doc.set_from_warehouse = "CBL - Campur Bahan - L"
		target_doc.set_warehouse = "GCP - Cor - L"
		target_doc.schedule_date = add_days(nowdate(),1)
		target_doc.work_order_cor = self.name
		
		temp = []
		# data = frappe._dict({
		# 'item_code': "",
		# 'uom': "",
		# 'qty': 0,
		# 'conversion_factor': 1,
		# 'schedule_date': add_days(nowdate(),1)
		# })
		for row in self.tabel_cor:
			if len(temp) < 1:
				temp.append(frappe._dict({
					"item_code": row.kadar,
					"qty":flt(row.berat_lilin) * frappe.get_doc("Data Logam", row.kadar).koefisien,
					"uom":"Gram",
					"conversion_factor":1,
					"schedule_date" : add_days(nowdate(),1)
				}))
				# frappe.msgprint(str(temp))
			else:
				for check in temp:
					frappe.msgprint(str(temp))
					# frappe.msgprint(str(check))
					# print(str(check))
					if check['item_code'] == row.kadar:
						check['qty'] = check['qty'] + (flt(row.berat_lilin) * frappe.get_doc("Data Logam", row.kadar).koefisien)
					else:
						status = True
						for check_2 in temp:
							if check_2['item_code'] == row.kadar:
								status = False
						if status:
							temp.append(frappe._dict({
								"item_code": row.kadar,
								"qty":flt(row.berat_lilin) * frappe.get_doc("Data Logam", row.kadar).koefisien,
								"uom":"Gram",
								"conversion_factor":1,
								"schedule_date" : add_days(nowdate(),1)
							}))
							for item in temp:
								baris_baru = {
								"item_code": item.item_code,
								"qty": item.qty,
								"uom":"Gram",
								"conversion_factor":1,
								"schedule_date" : add_days(nowdate(),1),
								"from_warehouse" : "CBL - Campur Bahan - L",
								"warehouse": "GCP - Cor - L"
								}
								target_doc.append("items",baris_baru)
							target_doc.flags.ignore_permission = True
							target_doc.save()
				
					
	def on_submit(self):

		target_doc3 = frappe.get_doc('Data Pohon Lilin', self.pohon_id)
		target_doc3.warehouse = "GCP - Cor - L"
		target_doc3.nomor_base_karet = self.nomor_base_karet
		target_doc3.ukuran_base_karet = self.ukuran_base_karet
		target_doc3.sprue_utama = self.sprue_utama
		baris_baru = {
				"warehouse": "GCP - Cor - L",
				"nomor_wo": self.name
			}
		target_doc3.append("lokasi",baris_baru)
		target_doc3.flags.ignore_permission = True
		target_doc3.save()
		
	@frappe.whitelist()
	def simpan_material(self):
		# source_doc = frappe.get_doc("Job Card Operator", self)
		for row in self.tabel_cor:
			if row.nomor_base_karet == self.nomor_base_karet:
				row.batch_cb_1 = self.batch_cb_1
				row.berat_batch_1 = self.berat_batch_1
				row.batch_cb_2 = self.batch_cb_2
				row.berat_batch_2 = self.berat_batch_2
				row.batch_cb_3 = self.batch_cb_3
				row.berat_batch_3 = self.berat_batch_3
		self.pohon_id = ""
		self.nomor_base_karet = ""
		self.batch_cb_1 = ""
		self.berat_batch_1 = 0
		self.batch_cb_2 = ""
		self.berat_batch_2 = 0
		self.batch_cb_3 = ""
		self.berat_batch_3 = 0

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_mr(doctype, txt, searchfield, start, page_len, filters=None):

	item_mr = frappe.get_list("Material Request Item", filters={'parent':filters.get("parent")}, fields=['name'])
	conditions = ""
	for x in item_mr:
		# frappe.msgprint(str(x))
		if conditions == "":
			conditions = "'{}'".format(x.name)
		else:
			conditions = "{},'{}'".format(conditions, x.name)
			
	items = []
	for item in item_mr:
		items.append(item.name)

	txt = ','.join('"%s"' % _ for _ in items)
	# frappe.msgprint(txt)
	return frappe.db.sql("""
			SELECT 
			mri.name, 
			mri.item_name,
			mri.item_code 
			FROM `tabMaterial Request` mr
			JOIN `tabMaterial Request Item` mri ON mri.parent = mr.name 
			WHERE TRUE
			AND mr.name = "{}"
			AND mri.name in ({})			
		""".format(filters.get("parent"),txt), {
		# 'txt': "%{}%".format(txt),
		# '_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})