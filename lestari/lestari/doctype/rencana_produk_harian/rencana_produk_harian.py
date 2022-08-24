# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today

class RencanaProdukHarian(Document):
	
	def on_submit(self):
		sumber_doc = self
		if sumber_doc.area == "Lilin - L":
			frappe.msgprint("Lilin")
			for row in sumber_doc.tabel_pohon:
				target_doc = frappe.new_doc("Data Pohon Lilin")
				target_doc.area = sumber_doc.area
				target_doc.proses = sumber_doc.proses
				target_doc.kadar = row.kadar
				# sumber_resep = frappe.db.get_list("Resep Mul Karet", filters={"final_product":row.produk})		
				sumber_resep = frappe.db.sql("""
				SELECT
				rubber_mould,
				hasil_inject,
				final_product,
				name
				FROM `tabResep Mul Karet`
				WHERE final_product = "{}"
				""".format(row.produk),as_dict=1)
				for col in sumber_resep:
					baris_baru={
						"no_spk":row.no_spk,
						"produk_id":row.produk,
						"mul_karet":col.rubber_mould,
						"resep_mul_karet":col.name,
						"qty":row.qty,
						"inject":col.hasil_inject,
						"logo":frappe.get_doc("Item",row.produk).brand
						}
					target_doc.append("resep",baris_baru)
				target_doc.flags.ignore_permissions = True
				target_doc.save()

		if sumber_doc.area == "GCP - L":
			# frappe.msgprint("Gips")
			
			target_doc1 = frappe.new_doc("Material Request")
			target_doc1.material_request_type = "Manufacture"
			target_doc1.schedule_date = add_days(today(),1)
			current_data = sumber_doc.tabel_gips
			sorted_data = []
			sorted_data = sorted(current_data, key = lambda i:(i.kadar, i.no_pohon))

			for row in sumber_doc.tabel_gips:	
				qty = flt(frappe.get_doc("Data Logam", row.kadar).koefisien) * flt(row.berat_pohon)
				item_name = frappe.get_doc("Item", row.kadar).item_name
				uom = frappe.get_doc("Item", row.kadar).stock_uom
				mr_item = {
					'item_code': row.kadar,
					'item_name': item_name,
					'schedule_date': add_days(today(),1),
					'warehouse': "Campur Bahan - L",
					'uom': uom,
					'qty': qty,
				}
				target_doc1.append("items",mr_item)
			target_doc1.flags.ignore_permissions = True
			target_doc1.save()
			no_mr = target_doc1.name

			target_doc = frappe.new_doc("Work Order Gips")
			target_doc.area = sumber_doc.area
			target_doc.proses = sumber_doc.proses
			target_doc.nomor_mr = no_mr
			for row in sorted_data:

				baris_baru = {
					'no_spk': row.no_spk,
					'no_pohon': row.no_pohon,
					'kadar': row.kadar,
					'tanggal_pohonan': row.tanggal_pohonan,
					'pohon_id': row.pohon_id,
					'jenis_sprue': row.jenis_sprue,
					'ukuran': row.ukuran,
					'berat_lilin': row.berat_lilin,
					'berat_batu': row.berat_batu,
					'berat_pohon': row.berat_pohon,
					'qty_permintaan': row.qty
				}
				target_doc.append("tabel_pohon",baris_baru)

			target_doc.flags.ignore_permissions = True
			target_doc.save()

def get_requested_item_qty(sales_order):
	return frappe._dict(frappe.db.sql("""
		select sales_order_item, sum(qty)
		from `tabMaterial Request Item`
		where docstatus = 1
			and sales_order = %s
		group by sales_order_item
	""", sales_order))

@frappe.whitelist()
def get_items_from_spk_produksi(source_name, target_doc=None):
	requested_item_qty = get_requested_item_qty(source_name)

	def update_item(source, target, source_parent):
		target.qty = source.get("qty")
		target.produk_id = source.get("produk_id")
		target.no_spk = source.get("no_spk")
		target.kadar = source.get("kadar")
		target.customer = source.get("customer")
		target.qty_isi_pohon = source.get("qty_isi_pohon")
		target.jumlah_pohon = source.get("jumlah_pohon")
		target.target_berat = source.get("target_berat")

	doc = get_mapped_doc("SPK Produksi", source_name, {
		"SPK Produksi": {
			"doctype": "Rencana Produk Harian",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"SPK Produksi Detail": {
			"doctype": "Rencana Produk Harian Lilin",
			"field_map": {
				"name": "spk_produksi_detail",
				"parent": "spk_produksi"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doc

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
	requested_item_qty = get_requested_item_qty(source_name)

	def update_item(source, target, source_parent):
		target.qty = source.get("qty")
		target.produk = source.get("item_code")
		target.no_spk = source_name
		target.kadar = frappe.get_doc("Item",source.get("item_code")).kadar
		target.logo = frappe.get_doc("Item",source.get("item_code")).brand
		item_groups = source.get("item_group")
		target.kategori = frappe.get_doc("Item Group", item_groups).parent_item_group
		# qty is for packed items, because packed items don't have stock_qty field
		# target.project = source_parent.project
		# target.qty = qty - requested_item_qty.get(source.name, 0)
		# target.stock_qty = flt(target.qty) * flt(target.conversion_factor)

	doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Rencana Produk Harian",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Packed Item": {
			"doctype": "Rencana Produk Harian Lilin",
			"field_map": {
				"parent": "sales_order",
				"uom": "stock_uom"
			},
			"postprocess": update_item
		},
		"Sales Order Item": {
			"doctype": "Rencana Produk Harian Lilin",
			"field_map": {
				"name": "sales_order_item",
				"parent": "sales_order"
			},
			"condition": lambda doc: not frappe.db.exists('Product Bundle', doc.item_code) and doc.stock_qty > requested_item_qty.get(doc.name, 0),
			"postprocess": update_item
		}
	}, target_doc)

	return doc

@frappe.whitelist()
def get_material_request(source_name, target_doc=None):

	def update_item(source, target, source_parent):
		
		target.qty = source.get("qty")
		target.produk = source.get("item_code")
		target.no_spk = source_name
		target.kadar = frappe.get_doc("Item",source.get("item_code")).kadar
		target.logo = frappe.get_doc("Item",source.get("item_code")).brand
		item_groups = source.get("item_group")
		target.kategori = frappe.get_doc("Item Group", item_groups).parent_item_group

	doc = get_mapped_doc("Material Request", source_name, {
		"Material Request": {
			"doctype": "Rencana Produk Harian",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Packed Item": {
			"doctype": "Rencana Produk Harian Lilin",
			"field_map": {
				"parent": "material_request",
				"uom": "stock_uom"
			},
			"postprocess": update_item
		},
		"Material Request Item": {
			"doctype": "Rencana Produk Harian Lilin",
			"field_map": {
				"name": "material_request_item",
				"parent": "material_request"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doc

@frappe.whitelist()
def get_data_gips(from_tanggal = None, to_tanggal = None, kadar = None, jenis_sprue = None):
	data = []
	# data.append({'tanggal_pohonan':tanggal_pohonan,'kadar':kadar,'kategori':kategori,'sub_kategori':sub_kategori})
	condition = ""
	if from_tanggal:
		condition += "AND"+" (fhwo.created_date between '"+from_tanggal+"'"
	if to_tanggal:
		condition += " AND '"+to_tanggal+"')"
	if kadar:
		condition += " AND fhwod.kadar = '"+kadar+"'"
	if jenis_sprue:
		condition += " AND fhwod.jenis_sprue = '"+jenis_sprue+"'"
	frappe.msgprint(condition)
	sumber_fhwo = frappe.db.sql("""
	SELECT
	fhwod.no_spk,
	fhwod.no_pohon,
	fhwod.tanggal_pohonan,
	fhwod.pohon_id,
	fhwod.kadar,
	fhwod.qty,
	fhwod.ukuran,
	fhwod.berat_lilin,
	fhwod.berat_batu,
	fhwod.berat_pohon,
	fhwod.jenis_sprue
	FROM `tabForm Hasil Work Order` fhwo
	JOIN `tabForm Hasil Work Order Detail` fhwod ON fhwod.parent = fhwo.name
	WHERE fhwo.docstatus = 1 {}
	""".format(condition),as_dict=1)

	return sumber_fhwo

@frappe.whitelist()
def make_form_hasilwo(source_name, target_doc=None):
	def update_item(source, target, source_parent):
		target.work_order_id = source_parent.work_order_id

	def set_missing_values(source, target):
		rph = frappe.get_doc(target)
		rph.work_order_id = source.work_order_id
		frappe.msgprint(source.work_order_id)

	doc = get_mapped_doc("Form Hasil Work Order", source_name, {
		"Form Hasil Work Order": {
			"doctype": "Rencana Produk Harian",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Form Hasil Work Order Detail": {
			"doctype": "Rencana Produk Harian Gips",
			"field_map": {
				"name": "form_hasil_work_order_detail",
				"parent": "form_hasil_work_order"
			},
			"postprocess": update_item
		}
	}, target_doc, set_missing_values)
	# frappe.msgprint(str(doc.area))
	doc.area = "GCP - L"
	doc.proses = "Persiapan"
	return doc