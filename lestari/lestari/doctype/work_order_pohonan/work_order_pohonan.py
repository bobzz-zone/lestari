# Copyright (c) 2021, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.reportview import get_match_cond, get_filters_cond

class WorkOrderPohonan(Document):
	def on_submit(self):
		sumber_doc = self
		target_doc = frappe.get_doc("Data Pohon Lilin", self.pohon_id)
		if target_doc.status == "Plan" and sumber_doc.docstatus == 1:
			target_doc.status = "Supermarket"
		elif target_doc.status == "Supermarket" and sumber_doc.docstatus == 1:
			target_doc.status = "Gips"
		elif target_doc.status == "Gips" and sumber_doc.docstatus == 1:
			target_doc.status = "Oven"
		elif target_doc.status == "Oven" and sumber_doc.docstatus == 1:
			target_doc.status = "Cor"
		elif target_doc.status == "Cor" and sumber_doc.docstatus == 1:
			target_doc.status = "Lebur"
		else:
			target_doc.status = "Potong Cor"
		target_doc.flags.ignore_permissions = True
		target_doc.save()

		target_doc2 = frappe.new_doc("Form Hasil Work Order")
		target_doc2.work_order = sumber_doc.name
		target_doc2.pohon_lilin	= sumber_doc.pohon_id
		target_doc2.status_tujuan = sumber_doc.status_pohonan
		target_doc2.warehouse_tujuan = sumber_doc.warehouse_wip
		berat_total = 0
		for row in sumber_doc.material:
			berat_total += int(row.berat)
		
		target_doc2.uom_total_berat_karet = "Gram"
		target_doc2.total_berat_batu = berat_total
		target_doc2.uom_total_berat_batu = "Gram"
		target_doc2.total_berat_karet = int(sumber_doc.berat_pohonan_lilin) - int(berat_total)
		target_doc2.net_total = sumber_doc.berat_pohonan_lilin
		target_doc2.uom_net_total = "Gram"
		target_doc2.flags.ignore_permissions = True
		target_doc2.save()

@frappe.whitelist()
def berat_material(no_dpl,no_wop):
	frappe.msgprint("berat_material")
	sumber_doc = frappe.get_doc("Work Order Pohonan", no_wop)
	target_doc = frappe.new_doc("Form Berat Material Pohon")
	target_doc.wo_id = no_wop
	target_doc.pohon_id = no_dpl
	target_doc.uom_berat = "Gram"
	sumber_batu = frappe.db.sql("""
		SELECT
		wopm.material,
		wopm.qty
		FROM `tabWork Order Pohonan Material` wopm
		WHERE wopm.parent = "{}"
		""".format(no_wop), as_dict=1)
	for batu in sumber_batu:
		baris_baru = {
				"batu": batu.material,
				"berat": 0,
				"berat_uom": "Gram",
				"qty": batu.qty,
				"uom_qty": batu.uom_qty
				}
		target_doc.append("material_batu",baris_baru)
	# target_doc.flags.ignore_permissions = True
	# target_doc.save()
	return target_doc.as_dict()

@frappe.whitelist()
def make_stock_entry(no_dpl,no_wop,status,serial_sprue):
	sumber_doc = frappe.get_doc("Work Order Pohonan", no_wop)
	target_doc = frappe.new_doc("Stock Entry")
	target_doc.stock_entry_type = "Material Transfer"
	if status == "Supermarket":
		sumber_sprue = frappe.db.sql("""
			SELECT
			sn.name,
			sn.warehouse,
			item.item_code,
			item.stock_uom
			FROM `tabSerial No` sn
			JOIN `tabItem` item ON item.item_name = sn.item_name
			WHERE sn.name = "{}"
			""".format(serial_sprue), as_dict=1)

		for row in sumber_sprue:
			baris_baru = {
				"item_code": row.item_code,
				"qty": 1,
				"uom" : row.stock_uom,
				"conversion_factor" : 1,
				"t_warehouse" : "Work In Progress - L",
				"s_warehouse" : row.warehouse,
				"serial_no" : serial_sprue
			}
			target_doc.append("items",baris_baru)
			
		sumber_material = frappe.db.sql("""
		SELECT DISTINCT
		pplm.material AS item_code,
		pplm.qty AS qty,
		pplm.uom_qty AS uom,
		dplr.resep_cetakan AS resep,
		itemdef.default_warehouse AS s_warehouse
		FROM `tabWork Order Pohonan` wop
		JOIN `tabData Pohon Lilin Resep` dplr ON dplr.parent = "{}"
		JOIN `tabResep Investment Lilin Batu` rilb ON rilb.parent = dplr.resep_cetakan
		JOIN `tabWork Order Pohonan Material` pplm ON pplm.material = rilb.batu
		JOIN `tabItem Default` itemdef ON itemdef.parent = pplm.material
		WHERE pplm.parent = "{}" ORDER BY pplm.material
		""".format(no_dpl,no_wop), as_dict=1)
		
		for row in sumber_material:

			serialqty = frappe.db.sql("""
			SELECT 
			qty
			FROM `tabData Pohon Lilin Resep`
			WHERE parent = "{}" and resep_cetakan = "{}"
			GROUP BY resep_cetakan
			""".format(no_dpl, row.resep), as_dict=1)

			baris_baru = {
					"item_code": row.item_code,
					"qty": row.qty * serialqty[0].qty,
					"uom" : row.uom,
					"conversion_factor" : 1,
					"t_warehouse" : "Work In Progress - L",
					"s_warehouse" : row.s_warehouse
					}
			target_doc.append("items",baris_baru)
			# frappe.msgprint(str(baris_baru))

		sumber_query = frappe.db.sql("""
		SELECT 
		ppls.rubber_mould,
		itemdef.default_warehouse,
		ppls.uom,
		COUNT(ppls.mul_id) AS qty,
		GROUP_CONCAT(DISTINCT ppls.mul_id) AS mul_id
		FROM `tabWork Order Pohonan Tools` ppls
		JOIN `tabItem Default` itemdef ON itemdef.parent = ppls.rubber_mould
		WHERE ppls.parent = "{}"
		GROUP BY ppls.rubber_mould
		ORDER BY GROUP_CONCAT(DISTINCT ppls.mul_id) ASC
		""".format(no_wop), as_dict=1)

		for row in sumber_query:
			rserial = row.mul_id
			# frappe.msgprint(str(rserial))
			serial = rserial.replace(",","\n")

			baris_baru = {
					"item_code": row.rubber_mould,
					"qty": row.qty,
					"uom" : row.uom,
					"conversion_factor" : 1,
					"t_warehouse" : "Work In Progress - L",
					"s_warehouse" : row.default_warehouse,
					"serial_no" : serial
					}
			target_doc.append("items",baris_baru)
	elif status == "Gips":
		frappe.msgprint("Gips")
	elif status == "Oven":
		frappe.msgprint("Oven")
	elif status == "Lebur":
		frappe.msgprint("Lebur")
	elif status == "Cor":
		frappe.msgprint("Cor")
	elif status == "Potong":
		frappe.msgprint("Potong")
	target_doc.flags.ignore_permissions = True
	target_doc.save()
	return target_doc.as_dict()

@frappe.whitelist()
def get_resep(doctype, txt, searchfield, start, page_len, filters=None):
	return frappe.db.sql("""
			SELECT rmk.name, 
			rmk.rubber_mould
			FROM `tabResep Mul Karet` rmk
			JOIN `tabData Pohon Lilin Resep` dplr ON dplr.resep_cetakan = rmk.name
			JOIN `tabData Pohon Lilin` dpl ON dpl.name = dplr.parent
			WHERE TRUE
			AND dpl.name = "{}"
			
		""".format(filters.get("parent")), {
		'txt': "%{}%".format(txt),
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})

@frappe.whitelist()
def get_mul(doctype, txt, searchfield, start, page_len, filters=None):

	conditions = ""

	for x in filters.get("child_list"):
		if conditions == "":
			conditions = "'{}'".format(x)
		else:
			conditions = "{},'{}'".format(conditions, x)

	return frappe.db.sql("""
			SELECT sn.name, 
			sn.item_code, 
			sn.item_name, 
			dpl.name AS dplname 
			FROM `tabSerial No` sn 
			JOIN `tabData Pohon Lilin Resep` dplr ON dplr.rubber_mould = sn.item_code 
			JOIN `tabData Pohon Lilin` dpl ON dpl.name = dplr.parent
			WHERE TRUE
			AND dpl.name = "{}"
			AND sn.item_code in ({})
			
			
		""".format(filters.get("dplname"),conditions), {
		'txt': "%{}%".format(txt),
		'_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})