# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormBeratMaterialPohon(Document):
	def on_submit(self):
		sumber_doc = self
		target_doc = frappe.get_doc("NTHKO Lilin", {"work_order_id":sumber_doc.work_order_id,"pohon_id":sumber_doc.pohon_id})
		frappe.msgprint(str(target_doc))
		target_doc.total_berat_base_karet = sumber_doc.berat_base_karet
		target_doc.total_berat_batu = sumber_doc.total_berat_batu
		target_doc.tabel_detail[0].berat_batu = sumber_doc.total_berat_batu
		for row in target_doc.tabel_batu:
			for col in self.material_batu:
				if col.batu == row.batu and col.mul_karet == row.mul_karet and col.warna_batu == row.warna_batu:
						row.berat = col.berat
		target_doc.flags.ignore_permissions = True
		target_doc.save()

		target_doc1 = frappe.new_doc("Stock Entry")
		target_doc1.stock_entry_type = "Material Transfer"
		target_doc1.employee_id = sumber_doc.employee_id
		target_doc1.to_warehouse = "Work In Progress - L"
		target_doc1.from_warehouse = "Inventory - L"
		target_doc1.remarks = self.name

		for row in sumber_doc.material_batu:

			baris_baru = {
				"item_code":row.batu,
				"qty":row.qty,
				"uom":frappe.get_doc("Item",row.batu).stock_uom,
				"conversion_factor":1,
				"allow_zero_valuation_rate":1,
				"item_group":frappe.get_doc("Item",row.batu).item_group,
				"t_warehouse":"Supermarket - L",
				"s_warehouse":"Lilin - L",
				"description":row.warna_batu
			}
			target_doc1.append("items",baris_baru)
			target_doc1.flags.ignore_permissions = True
			# # target_doc1.docstatus = 1
			target_doc1.save()

	# def validate(self):		
	# 	# frappe.msgprint(self.wo_id)
	# 	if self.wo_id:
	# 		# frappe.msgprint("get_fbmp")
	# 		# get_fbmp(self.name,self.wo_id)
	# 		sumber_doc = self
	# 		target_doc = frappe.get_doc("Work Order Pohonan", self.wo_id)

	# 		berat_total = 0
	# 		for row in target_doc.material:
	# 			for col in sumber_doc.material_batu:
	# 				if row.material == col.batu:
	# 					frappe.msgprint(str(col.berat))
	# 					berat_total += int(col.berat)
	# 					row.berat = col.berat

	# 		berat_total += int(sumber_doc.berat_base_karet)
	# 		berat_total = target_doc.berat_pohonan_lilin - berat_total
	# 		target_doc.berat_wax_pohonan_lilin = berat_total
	# 		target_doc.uom_berat = "Gram"
	# 		target_doc.flags.ignore_permissions = True
	# 		target_doc.save()

@frappe.whitelist()
def get_fbmp(no_fbmp,no_wo):
	sumber_doc = frappe.get_doc("Form Berat Material Pohon", no_fbmp)
	target_doc = frappe.get_doc("Work Order Pohonan", no_wo)

	for row in target_doc.material:
		for col in sumber_doc.material_batu:
			if row.material == col.batu:
				frappe.msgprint(str(col.berat))
				row.berat = col.berat

	target_doc.save()
	# sumber_batu = frappe.throw("""
	# SELECT
	# batu,
	# berat
	# FROM `tabForm Berat Material Batu`
	# WHERE parent = "{}"
	# """.format(no_fbmp))
	# sumber_batu = frappe.get_doc("Form Berat Material Batu", {"parent":no_fbmp}, ['batu','berat'])
	# frappe.msgprint(str(sumber_batu))
	# for row in sumber_batu:
	# 	doc = frappe.get_doc("Work Order Pohonan Material", {"parent":no_wo,"material":row.batu})
	# 	doc.berat = row.berat
	# 	doc.form_berat_material_pohon = no_fbmp
	# 	doc.save()
	# 	frappe.db.sql("""
	# 	Update `tabWork Order Pohonan Material`
	# 	SET berat = "{}", form_berat_material_pohon = "{}"
	# 	WHERE parent = "{}" and material = "{}"
	# 	""".format(row.berat,no_fbmp,no_wo,row.batu))
	# frappe.db.commit()
		# frappe.db.set_value('Work Order Pohonan Material', no_wo, {
		# 	'material': row.batu,
		# 	'berat': row.berat
		# })
		# frappe.msgprint(("""
		# Update `tabWork Order Pohonan Material`
		# SET berat = "{}", form_berat_material_pohon = "{}"
		# WHERE parent = "{}" and material = "{}"
		# """.format(row.berat,no_fbmp,no_wo,row.batu)))
		
		
	# target_doc.flags.ignore_permissions = True
	# target_doc.save()
