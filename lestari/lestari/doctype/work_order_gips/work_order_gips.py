# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from frappe.utils import flt, add_days, today
from operator import itemgetter

class WorkOrderGips(Document):
	def on_submit(self):
		for dpl in self.tabel_pohon:
			target_doc3 = frappe.get_doc('Data Pohon Lilin', dpl.pohon_id)
			target_doc3.warehouse = "Gips - L"
			target_doc3.nomor_base_karet = dpl.nomor_base_karet
			target_doc3.ukuran_base_karet = dpl.ukuran_base_karet
			baris_baru = {
					"warehouse": "Gips - L",
					"nomor_wo": self.name
				}
			target_doc3.append("lokasi",baris_baru)
			target_doc3.flags.ignore_permission = True
			target_doc3.save()
			
	@frappe.whitelist()
	def generate_form_oven1(self):
		source_doc = self
		frappe.msgprint(str(int(len(source_doc.tabel_pohon))//50))
		mesin_oven = frappe.get_all("Data Mesin Oven", fields=['name','nomor_oven'], order_by='name')
		for col in mesin_oven:
			for row in source_doc.tabel_pohon:
				if not row.mesin_oven:
					if row.idx <= (50*int(col.nomor_oven)):	
						frappe.msgprint(col.name)
						row.mesin_oven = col.name
		source_doc.flags.ignore_permissions = True
		source_doc.save()
		source_doc.reload()

	@frappe.whitelist()
	def generate_form_gips1(self):
		source_doc = self
		mesin_gips = frappe.get_list("Data Mesin Gips", fields=['name', 'ukuran_mesin', 'kapasitas_mesin'])
		list_ukuran_mesin = []
		data_mesin = frappe._dict({
			'name': "",
			'ukuran_mesin_gips': 0,
			'kapasitas_mesin_gips': 0
		})

		for col in mesin_gips:
			data_mesin = frappe._dict({
			'name': col.name,
			'ukuran_mesin_gips': col.ukuran_mesin,
			'kapasitas_mesin_gips': col.kapasitas_mesin
		})
			list_ukuran_mesin.append(frappe._dict({
							"name": data_mesin.name,
							"ukuran_mesin_gips": data_mesin.ukuran_mesin_gips,
							"kapasitas_mesin_gips": data_mesin.kapasitas_mesin_gips
						}))

		#frappe.msgprint(str(len_source))
		if int(len(source_doc.tabel_pohon)) in [200,150,100,50]:
			# frappe.msgprint("Data Gips 200")
			#mesin 8 -> besar 4, kecil / sedang 4
			#mesin 6 -> besar 3 , kecil / sedang 3
			pohon_kecil=[]
			pohon_besar=[]
			for row in source_doc.tabel_pohon:
				if row.ukuran_base_karet=="Besar":
					pohon_besar.append(row)
				else:
					pohon_kecil.append(row)
			if int(len(source_doc.tabel_pohon)) == 200:
				batch_6 = 12
				batch_8 = 16
			elif int(len(source_doc.tabel_pohon)) == 150:
				batch_6 = 9
				batch_8 = 12
			elif int(len(source_doc.tabel_pohon)) == 100:
				batch_6 = 6
				batch_8 = 8
			elif int(len(source_doc.tabel_pohon)) == 50:
				batch_6 = 4
				batch_8 = 4
			batch_no=1
			#validasi pohon besar tidak boleh lebih dari maximal
			if (batch_8*4)+(batch_6*3)<len(pohon_besar):
				frappe.throw("Jumlah Pohon Besar Terlalu banyak")
			total_used_besar=0
			total_used_kecil=0
			#generate untuk batch mesin 8
			for count in range(0,batch_8):
				current_start=total_used_besar
				current_start_kecil=total_used_besar
				total_berat_batch=0
				skipped=0
				for index in range(current_start,current_start+4):
					if index>=len(pohon_besar):
						skipped+=1
						continue
					row=pohon_besar[index]
					total_used_besar+=1
					total_berat_batch = total_berat_batch + flt(row.sub_total_berat)

					source_doc.append("tabel_batch", frappe._dict({
												'no_batch_gips': batch_no,
												'mesin_gips': "Mesin-8",
												'nomor_base_karet': row.nomor_base_karet,
												'pohon_id': row.pohon_id,
												'kadar': row.kadar,
												'ukuran_base_karet': row.ukuran_base_karet,
												'sub_total_berat': row.sub_total_berat,
												'batch_total': total_berat_batch
											}))
				for index in range(current_start_kecil,current_start_kecil+4+skipped):
					row=pohon_kecil[index]
					#total_berat_batch = total_berat_batch + flt(row['sub_total_berat'])
					total_used_kecil+=1
					source_doc.append("tabel_batch", frappe._dict({
												'no_batch_gips': batch_no,
												'mesin_gips': "Mesin-8",
												'nomor_base_karet': row.nomor_base_karet,
												'pohon_id': row.pohon_id,
												'kadar': row.kadar,
												'ukuran_base_karet': row.ukuran_base_karet,
												'sub_total_berat': row.sub_total_berat,
												'batch_total': total_berat_batch
											}))
				batch_no+=1
			#generate untuk batch mesin 6
			for count in range(0,batch_6):
				current_start=total_used_besar
				current_start_kecil=total_used_besar
				total_berat_batch=0
				skipped=0
				for index in range(current_start,current_start+3):
					if index>=len(pohon_besar):
						skipped+=1
						continue
					row=pohon_besar[index]
					total_used_besar+=1
					total_berat_batch = total_berat_batch + flt(row.sub_total_berat)
					source_doc.append("tabel_batch", frappe._dict({
												'no_batch_gips': batch_no,
												'mesin_gips': "Mesin-6",
												'nomor_base_karet': row.nomor_base_karet,
												'pohon_id': row.pohon_id,
												'kadar': row.kadar,
												'ukuran_base_karet': row.ukuran_base_karet,
												'sub_total_berat': row.sub_total_berat,
												'batch_total': total_berat_batch
											}))
				for index in range(current_start_kecil,current_start_kecil+3+skipped):
					row=pohon_kecil[index]
					#total_berat_batch = total_berat_batch + flt(row['sub_total_berat'])
					total_used_kecil+=1
					source_doc.append("tabel_batch", frappe._dict({
												'no_batch_gips': batch_no,
												'mesin_gips': "Mesin-6",
												'nomor_base_karet': row.nomor_base_karet,
												'pohon_id': row.pohon_id,
												'kadar': row.kadar,
												'ukuran_base_karet': row.ukuran_base_karet,
												'sub_total_berat': row.sub_total_berat,
												'batch_total': total_berat_batch
											}))
				batch_no+=1
			source_doc.save()
		else:
			frappe.throw("Silakan Gunakan Section Detail Gips")

	@frappe.whitelist()
	def generate_jenis_gips1(self):
		source_doc = self
		j_gips = frappe.get_doc("Data Gips", source_doc.jenis_gips)
		tot_berat_air = 0
		tot_berat_gips = 0
		tot_bahan = 0
		for row in source_doc.tabel_pohon:
			row.jenis_gips = j_gips.name
			for col in j_gips.gips:
				if row.ukuran_base_karet == col.ukuran_base_karet and col.qty == 1:
					row.vol_air = col.air__cc_
					tot_berat_air = tot_berat_air + col.air__cc_
					row.berat_gips = col.gips__gram_
					tot_berat_gips = tot_berat_gips + col.gips__gram_
					row.sub_total_berat = col.air__cc_ + col.gips__gram_

		frappe.msgprint(tot_berat_air)
		tot_bahan = tot_berat_air + tot_berat_gips
		source_doc.total_berat_air = tot_berat_air
		source_doc.total_berat_gips = tot_berat_gips
		source_doc.total_bahan = tot_bahan
		source_doc.flags.ignore_permissions = True
		source_doc.save()
		source_doc.reload()
	
	@frappe.whitelist()
	def generate_work_order_cor1(self):	
		source_doc = self
		frappe.msgprint(str(int(len(source_doc.tabel_pohon))//50))
		mesin_cor = frappe.get_all("Data Mesin Cor", fields=['name','nomor_mesin'], order_by='name')
		for col in mesin_cor:
			target_doc = frappe.new_doc("Work Order Cor")
			target_doc.nomor_mesin = col.name
			for row in source_doc.tabel_pohon:
				if not row.mesin_cor:
					if row.idx <= (50*int(col.nomor_mesin)):	
						# frappe.msgprint(col.name)
						row.mesin_cor = col.name
						baris_baru = {
						"nomor_base_karet": row.nomor_base_karet,
						"pohon_id": row.pohon_id,
						"kadar": row.kadar,
						"no_spk": row.no_spk,
						"berat_pohon": row.berat_pohon,
						"berat_lilin": row.berat_lilin,
						"berat_batu": row.berat_batu
						}
						target_doc.append("tabel_cor",baris_baru)
						target_doc.flags.ignore_permission = True
						target_doc.save()

		source_doc.flags.ignore_permissions = True
		source_doc.save()

@frappe.whitelist()
def generate_form_oven(name):
	source_doc = frappe.get_doc("Work Order Gips", name)
	frappe.msgprint(str(int(len(source_doc.tabel_pohon))//50))
	mesin_oven = frappe.get_all("Data Mesin Oven", fields=['name','nomor_oven'], order_by='name')
	for col in mesin_oven:
		for row in source_doc.tabel_pohon:
			if not row.mesin_oven:
				if row.idx <= (50*int(col.nomor_oven)):	
					frappe.msgprint(col.name)
					row.mesin_oven = col.name
	source_doc.flags.ignore_permissions = True
	source_doc.save()

@frappe.whitelist()
def generate_work_order_cor(name):
	source_doc = frappe.get_doc("Work Order Gips", name)	
	frappe.msgprint(str(int(len(source_doc.tabel_pohon))//50))
	mesin_cor = frappe.get_all("Data Mesin Cor", fields=['name','nomor_mesin'], order_by='name')
	for col in mesin_cor:
		target_doc = frappe.new_doc("Work Order Cor")
		target_doc.nomor_mesin = col.name
		for row in source_doc.tabel_pohon:
			if not row.mesin_cor:
				if row.idx <= (50*int(col.nomor_mesin)):	
					frappe.msgprint(col.name)
					row.mesin_cor = col.name
					baris_baru = {
					"nomor_base_karet": row.nomor_base_karet,
					"pohon_id": row.pohon_id,
					"kadar": row.kadar,
					"no_spk": row.no_spk
					}
					target_doc.append("tabel_cor",baris_baru)
					target_doc.flags.ignore_permission = True
					target_doc.save()

	source_doc.flags.ignore_permissions = True
	source_doc.save()

@frappe.whitelist()
def kapasitas_mesin_gips(mesin_gips):
	kapasitas_mesin = frappe.get_doc("Data Mesin Gips", mesin_gips)

	return kapasitas_mesin

@frappe.whitelist()
def generate_form_gips(name):
	source_doc = frappe.get_doc("Work Order Gips", name)
	
	list_ukuran = []
	data = frappe._dict({
		'kadar': "",
		'ukuran_base_karet': "",
		'qty': 0
	})

	for row in sorted(source_doc.tabel_pohon, key = lambda i:(i.kadar, i.ukuran_base_karet)):
		
		if data.kadar == "":
			data.kadar = row.kadar
		if data.ukuran_base_karet == "":
			data.ukuran_base_karet = row.ukuran_base_karet

		if data.kadar == row.kadar:
			if data.ukuran_base_karet == row.ukuran_base_karet:
				data.qty += 1
			else:
				list_ukuran.append(frappe._dict({
						"kadar": data.kadar,
						"ukuran_base_karet": data.ukuran_base_karet,
						"qty": data.qty
					}))
				data.ukuran_base_karet = row.ukuran_base_karet
				data.qty = 1
		else:
			list_ukuran.append(frappe._dict({
						"kadar": data.kadar,
						"ukuran_base_karet": data.ukuran_base_karet,
						"qty": data.qty
					}))
			data.kadar = row.kadar
			data.ukuran_base_karet = row.ukuran_base_karet
			data.qty = 1

	list_ukuran.append(frappe._dict({
						"kadar": data.kadar,
						"ukuran_base_karet": data.ukuran_base_karet,
						"qty": data.qty
					}))
	
	html = "<table>"
	for row in sorted(list_ukuran, key = lambda i:(i.kadar, i.ukuran_base_karet)):
		html += "<tr><td>Kadar</td><td>:</td><td>{}</td></tr><tr><td>Ukuran</td><td>:</td><td>{}</td></tr><tr><td>Qty</td><td>:</td><td>{}</td></tr>".format(row.kadar,row.ukuran_base_karet,row.qty)

	html += "</table>"
	# frappe.msgprint(html)	

	mesin_gips = frappe.get_list("Data Mesin Gips", fields=['name', 'ukuran_mesin', 'kapasitas_mesin'])

	list_ukuran_mesin = []
	data_mesin = frappe._dict({
		'name': "",
		'ukuran_mesin_gips': 0,
		'kapasitas_mesin_gips': 0
	})

	for col in mesin_gips:
		data_mesin = frappe._dict({
		'name': col.name,
		'ukuran_mesin_gips': col.ukuran_mesin,
		'kapasitas_mesin_gips': col.kapasitas_mesin
	})
		list_ukuran_mesin.append(frappe._dict({
						"name": data_mesin.name,
						"ukuran_mesin_gips": data_mesin.ukuran_mesin_gips,
						"kapasitas_mesin_gips": data_mesin.kapasitas_mesin_gips
					}))

	#frappe.msgprint(str(len_source))
	if int(len(source_doc.tabel_pohon)) == 200:
		# frappe.msgprint("Data Gips 200")
		#mesin 8 -> besar 4, kecil / sedang 4
		#mesin 6 -> besar 3 , kecil / sedang 3
		pohon_kecil=[]
		pohon_besar=[]
		for row in source_doc.tabel_pohon:
			if row.ukuran_base_karet=="Besar":
				pohon_besar.append(row)
			else:
				pohon_kecil.append(row)

		batch_6 = 12
		batch_8 = 16
		batch_no=1
		#validasi pohon besar tidak boleh lebih dari maximal
		if (batch_8*4)+(batch_6*3)<len(pohon_besar):
			frappe.throw("Jumlah Pohon Besar Terlalu banyak")
		total_used_besar=0
		total_used_kecil=0
		#generate untuk batch mesin 8
		for count in range(0,batch_8):
			current_start=total_used_besar
			current_start_kecil=total_used_besar
			total_berat_batch=0
			skipped=0
			for index in range(current_start,current_start+4):
				if index>=len(pohon_besar):
					skipped+=1
					continue
				row=pohon_besar[index]
				total_used_besar+=1
				total_berat_batch = total_berat_batch + flt(row.sub_total_berat)

				source_doc.append("tabel_batch", frappe._dict({
											'no_batch_gips': batch_no,
											'mesin_gips': "Mesin-8",
											'nomor_base_karet': row.nomor_base_karet,
											'pohon_id': row.pohon_id,
											'kadar': row.kadar,
											'ukuran_base_karet': row.ukuran_base_karet,
											'sub_total_berat': row.sub_total_berat,
											'batch_total': total_berat_batch
										}))
			for index in range(current_start_kecil,current_start_kecil+4+skipped):
				row=pohon_kecil[index]
				#total_berat_batch = total_berat_batch + flt(row['sub_total_berat'])
				total_used_kecil+=1
				source_doc.append("tabel_batch", frappe._dict({
											'no_batch_gips': batch_no,
											'mesin_gips': "Mesin-8",
											'nomor_base_karet': row.nomor_base_karet,
											'pohon_id': row.pohon_id,
											'kadar': row.kadar,
											'ukuran_base_karet': row.ukuran_base_karet,
											'sub_total_berat': row.sub_total_berat,
											'batch_total': total_berat_batch
										}))
			batch_no+=1
		#generate untuk batch mesin 6
		for count in range(0,batch_6):
			current_start=total_used_besar
			current_start_kecil=total_used_besar
			total_berat_batch=0
			skipped=0
			for index in range(current_start,current_start+3):
				if index>=len(pohon_besar):
					skipped+=1
					continue
				row=pohon_besar[index]
				total_used_besar+=1
				total_berat_batch = total_berat_batch + flt(row.sub_total_berat)
				source_doc.append("tabel_batch", frappe._dict({
											'no_batch_gips': batch_no,
											'mesin_gips': "Mesin-6",
											'nomor_base_karet': row.nomor_base_karet,
											'pohon_id': row.pohon_id,
											'kadar': row.kadar,
											'ukuran_base_karet': row.ukuran_base_karet,
											'sub_total_berat': row.sub_total_berat,
											'batch_total': total_berat_batch
										}))
			for index in range(current_start_kecil,current_start_kecil+3+skipped):
				row=pohon_kecil[index]
				#total_berat_batch = total_berat_batch + flt(row['sub_total_berat'])
				total_used_kecil+=1
				source_doc.append("tabel_batch", frappe._dict({
											'no_batch_gips': batch_no,
											'mesin_gips': "Mesin-6",
											'nomor_base_karet': row.nomor_base_karet,
											'pohon_id': row.pohon_id,
											'kadar': row.kadar,
											'ukuran_base_karet': row.ukuran_base_karet,
											'sub_total_berat': row.sub_total_berat,
											'batch_total': total_berat_batch
										}))
			batch_no+=1
		source_doc.save()

@frappe.whitelist()
def generate_jenis_gips(name,jenis_gips):
	source_doc = frappe.get_doc("Work Order Gips", name)
	j_gips = frappe.get_doc("Data Gips", jenis_gips)
	tot_berat_air = 0
	tot_berat_gips = 0
	tot_bahan = 0
	for row in source_doc.tabel_pohon:
		row.jenis_gips = j_gips.name
		for col in j_gips.gips:
			if row.ukuran_base_karet == col.ukuran_base_karet and col.qty == 1:
				row.vol_air = col.air__cc_
				tot_berat_air = tot_berat_air + col.air__cc_
				row.berat_gips = col.gips__gram_
				tot_berat_gips = tot_berat_gips + col.gips__gram_
				row.sub_total_berat = col.air__cc_ + col.gips__gram_

	frappe.msgprint(tot_berat_air)
	tot_bahan = tot_berat_air + tot_berat_gips
	source_doc.total_berat_air = tot_berat_air
	source_doc.total_berat_gips = tot_berat_gips
	source_doc.total_bahan = tot_bahan
	source_doc.flags.ignore_permissions = True
	source_doc.save()
	return source_doc.as_dict()
	# source_doc.reload()

@frappe.whitelist()
def make_wo_gips(source_name, target_doc=None):
	
	def update_item(source, target, source_parent):
		target.no_spk = source.get('no_spk')
		target.pohon_id = source.get('pohon_id')

	doc = get_mapped_doc("RPH Gips", source_name, {
		"RPH Gips": {
			"doctype": "Work Order Gips",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Packed Item": {
			"doctype": "Work Order Gips Pohon",
			"field_map": {
				"parent": "rph_gips"
			},
			"postprocess": update_item
		},
		"RPH Gips Detail": {
			"doctype": "Work Order Gips Pohon",
			"field_map": {
				"name": "rph_gips_detail",
				"parent": "rph_gips"
			},
			"postprocess": update_item
		}
	}, target_doc)

	return doc
