# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document

class PetaOven(Document):
	@frappe.whitelist()
	def after_save(self):
		max_details = {
			"Emas": 25,
			"Perak": 6,
			"Direct Casting": 12
		}

		# Get the maximum allowed details for the type_pohonan
		max_allowed = max_details.get(self.type_pohonan)

		if max_allowed and len(self.details) > max_allowed:
			frappe.msgprint(f"Maximum {max_allowed} details allowed for {self.type_pohonan}")
		
	@frappe.whitelist()
	def get_spk_gips(self):
		# frappe.msgprint("test")
		list_spk = frappe.db.get_list("Work Order Gips", filters={"docstatus":0}, order_by="tanggal_wo DESC")
		for row in list_spk:
			used = 0
			total = 0
			doc = frappe.get_doc("Work Order Gips", row.name)
			for col in doc.tabel_pohon:
				total += 1
				if col.used == 1:
					used += 1
			baris_baru = {
				"spk_gips": row.name,
				"id_spko_gips": doc.id_spko_gips,
				"transaction_date": doc.tanggal_wo,
				"total_pohonan": total,
				"total_pohonan_unused": total - used,
				"total_berat": doc.total_berat_fg
			}
			# frappe.msgprint(str(baris_baru))
			self.append("list_spk", baris_baru)

	@frappe.whitelist()
	def get_spk_gips_details(self):
		# Create a list to store the rows that will be added
		rows_to_add = []
		for row in self.list_spk:
			doc = frappe.get_doc("Work Order Gips", row.spk_gips)
			
			for col in doc.tabel_pohon:
				if col.used != 1:
					col_dic = col.as_dict()
					col_dic.pop('idx', None)
					if self.type_pohonan == "Emas" or self.type_pohonan == "Perak":
						# Exclude rows where nomor_base_karet starts with 'E' or 'D'
						if not col_dic.nomor_base_karet.startswith(('E', 'D')):
							rows_to_add.append(col_dic)
					if self.type_pohonan == "Direct Casting":
						if col_dic.nomor_base_karet.startswith(('E', 'D')):
							rows_to_add.append(col_dic)
			
		# Function to extract numeric part from 'kadar'
		def extract_numeric_kadar(kadar):
			if isinstance(kadar, str):  # Check if kadar is a string
				match = re.search(r'(\d+)', kadar)  # Extract numeric part
				return int(match.group(0)) if match else 0  # Default to 0 if no match
			return 0  # Default to 0 if kadar is not a string

		# Function to extract numeric part from 'nomor_base_karet'
		def extract_karet_num(val):
			match = re.search(r'(\D+)(\d+)', val)
			return match.group(1), int(match.group(2)) if match else (val, 0)

		# Sort the rows based on 'kadar' (using the new function) and 'nomor_base_karet' in descending order
		sorted_rows = sorted(rows_to_add, key=lambda x: (
			extract_numeric_kadar(x['kadar']),  # Sort 'kadar' numerically
			extract_karet_num(x['nomor_base_karet'])  # Sort 'nomor_base_karet'
		), reverse=True)  # Set reverse=True for descending order
		
		# Append the sorted rows to the details table, excluding 'idx'
		# for sorted_row in sorted_rows:
		# 	if self.type_pohonan == "Emas":
		# 		if sorted_row['kadar']:
		# 			# Remove 'idx' from the row before appending
		# 			# sorted_row.pop('idx', None)  # Safely remove 'idx' if it exists
		# 			# if self.type_pohonan == "Emas":
		# 			self.append("details", sorted_row)
		# 	if self.type_pohonan == "Perak":
		# 		self.append("details", sorted_row)
		
		# Save and reload the document to reflect changes
		return sorted_rows