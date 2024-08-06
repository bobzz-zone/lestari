import json
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.utils import cint, cstr, flt, get_link_to_form, getdate, new_line_sep, nowdate, unique
from six import string_types

def generate_gold_log():
	data = frappe.db.sql("select name from `tabGold Payment` where docstatus=1",as_list=1)
	for row in data:
		doc = frappe.get_doc("Gold Payment",row[0])
		doc.generate_gold_log()
def generate_gold_log2():
	data = frappe.db.sql("select name from `tabGold Invoice` where docstatus=1",as_list=1)
	for row in data:
		doc = frappe.get_doc("Gold Invoice",row[0])
		doc.generate_gold_log()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	cond=""
	if filters.get("item_group_parent"):
		cond="""{} and item_group_parent="{}" """.format(cond,filters.get("item_group_parent"))
	if filters.get("item_group"):
		cond="""{} and item_group="{}" """.format(cond,filters.get("item_group"))
	if filters.get("is_purchase_item"):
		cond="""{} and is_purchase_item="{}" """.format(cond,filters.get("is_purchase_item"))
	if filters.get("is_stock_item"):
		cond="""{} and is_stock_item="{}" """.format(cond,filters.get("is_stock_item"))
	if filters.get("is_fixed_asset"):
		cond="""{} and is_fixed_asset="{}" """.format(cond,filters.get("is_fixed_asset"))
	if filters.get("prod_con"):
		cond=""" {} and idproduct {}""".format(cond,filters.get("prod_con"))
	cond2 = ""
	if txt!="":
		cond2=""" and (name like "%{0}%" or item_name like "%{0}%") """.format(txt)
	return frappe.db.sql("""select name , item_name , item_group from tabItem where disabled=0 {0}  
			 and (name LIKE %(txt)s or item_name LIKE %(txt)s )  limit %(start)s, %(page_len)s 
			""".format(cond,cond2),
			{"txt": "%%%s%%" % txt,"start": start,"page_len": page_len},as_dict=as_dict)

def get_fields(doctype, fields=None):
    if fields is None:
        fields = []
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and meta.title_field.strip() not in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_material_requests_to_be_ordered(doctype, txt, searchfield, start, page_len, filters, as_dict):
    doctype = "Material Request"
    fields = get_fields(doctype, ["name", "idmaterial_request", "material_request_type", "transaction_date", "department"])

    return frappe.db.sql(
        """
        select {fields}
        from `tabMaterial Request`
        where `tabMaterial Request`.`{key}` like {txt} and
            `tabMaterial Request`.docstatus = 1
            and `tabMaterial Request`.per_ordered < 100
            and exists (
                select 1
                from `tabMaterial Request Item`
                where `tabMaterial Request Item`.parent = `tabMaterial Request`.name
                and `tabMaterial Request Item`.docstatus = 1
                and `tabMaterial Request Item`.ordered_qty < `tabMaterial Request Item`.qty
            )
            {fcond}
            {mcond} 
        order by `tabMaterial Request`.`{key}` desc 
        limit {page_len} 
        offset {start}
        """.format(
            fields=", ".join([f"`tabMaterial Request`.{f}" for f in fields]),
            key=searchfield,
            fcond=get_filters_cond(doctype, filters, []),
            mcond=get_match_cond(doctype),
            start=start,
            page_len=page_len,
            txt="%(txt)s",
        ),
        {"txt": ("%%%s%%" % txt)},
        as_dict=as_dict,
    )

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None, args=None):
	def update_item(obj, target, source_parent):
		qty = (
			flt(flt(obj.stock_qty) - flt(obj.ordered_qty)) / target.conversion_factor
			if flt(obj.stock_qty) > flt(obj.ordered_qty)
			else 0
		)
		target.qty = qty
		target.transfer_qty = qty * obj.conversion_factor
		target.conversion_factor = obj.conversion_factor
		target.ordinal = obj.ordinal

		if (
			source_parent.material_request_type == "Material Transfer"
			or source_parent.material_request_type == "Customer Provided"
		):
			target.t_warehouse = obj.warehouse
		else:
			target.s_warehouse = obj.warehouse

		if source_parent.material_request_type == "Customer Provided":
			target.allow_zero_valuation_rate = 1

		if source_parent.material_request_type == "Material Transfer":
			target.s_warehouse = obj.from_warehouse

	def set_missing_values(source, target):
		# target.purpose = source.material_request_type
		target.from_warehouse = source.set_from_warehouse
		target.to_warehouse = source.set_warehouse

		if source.job_card:
			target.purpose = "Material Transfer for Manufacture"

		if source.material_request_type == "Customer Provided":
			target.purpose = "Material Receipt"

		target.set_transfer_qty()
		target.set_actual_qty()
		target.calculate_rate_and_amount(raise_error_if_no_rate=False)
		# target.stock_entry_type = target.purpose
		target.set_job_card_data()

		if source.job_card:
			job_card_details = frappe.get_all(
				"Job Card", filters={"name": source.job_card}, fields=["bom_no", "for_quantity"]
			)

			if job_card_details and job_card_details[0]:
				target.bom_no = job_card_details[0].bom_no
				target.fg_completed_qty = job_card_details[0].for_quantity
				target.from_bom = 1

	def validasi_item(doc):
		if not (args and args.get("filtered_children")):
			return flt(doc.ordered_qty, doc.precision("ordered_qty")) < flt(doc.stock_qty, doc.precision("ordered_qty"))
		return doc.name in args.get("filtered_children")

	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Stock Entry",
				"field_map": {
					"employee_id" :"employee",
				},
				"field_no_map":["employee_id"],
				"validation": {
					"docstatus": ["=", 1],
					"material_request_type": [
						"in",
						["Material Transfer", "Material Issue", "Customer Provided"],
					],
				},
			},
			"Material Request Item": {
				"doctype": "Stock Entry Detail",
				"field_map": {
					"name": "material_request_item",
					"parent": "material_request",
					"uom": "stock_uom",
					"job_card_item": "job_card_item",
				},
				"postprocess": update_item,
				"condition": validasi_item,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist

@frappe.whitelist()
def get_recent_material_requests():
	return frappe.db.get_list('Material Request', 
		filters={
			'docstatus': 1,
			'material_request_type': ['in', ["Material Transfer", "Material Issue", "Customer Provided"]],
			'status': ['not in', ["Transferred", "Issued", "Cancelled", "Stopped"]]
		},
		fields=['name', 'material_request_type', 'customer', 'department', 'schedule_date', 'creation'],
		order_by='creation desc'
	)

@frappe.whitelist()
def patching_goldselling_top():
	# 1. cancel list gold Payment
	# 2. Rubah status menjadi draft
	# 3. rubah tutupan
	# 4. cancel list customer deposit 
	# 5. rubah status menjadi draft
	# 6. rubah tutupan
	# 7. submit customer deposit
	# 8. submit gold Payment

	list_gp = [ 
	{"gold_payment":"GP01120","customer_deposit":"CD-24-00208","tutupan":"1001000"}, 
	{"gold_payment":"GP01120","customer_deposit":"CD-24-00209","tutupan":"1002500"}, 
	{"gold_payment":"GP01120","customer_deposit":"CD-24-00210","tutupan":"993000"}, 
	{"gold_payment":"GP01163","customer_deposit":"CD-24-00211","tutupan":"1004500"}, 
	{"gold_payment":"GP01163","customer_deposit":"CD-24-00212","tutupan":"1004000"}, 
	{"gold_payment":"GP01163","customer_deposit":"CD-24-00213","tutupan":"1011000"}
	]
	index = 0
	print(str(len(list_gp)))
	for row in list_gp:
		print(str(row['gold_payment']))
		index += 1
		print(index)
		doc = frappe.get_doc("Gold Payment", row['gold_payment'])
		doc.cancel()
		frappe.db.sql("""UPDATE `tabGold Payment` SET docstatus = 0 WHERE name = '{}' """.format(row['gold_payment']),debug=1)
		frappe.db.commit()
		# doc.tutupan = doc['tutupan']
		frappe.db.sql("""UPDATE `tabGold Payment` SET tutupan = {0} WHERE name = '{1}' """.format(row['tutupan'],row['gold_payment']),debug=1)
		doc.flags.ignore_permissions = True
		doc.save()
		cd = frappe.get_doc("Customer Deposit", row['customer_deposit'])
		cd.cancel()
		frappe.db.sql("""UPDATE `tabCustomer Deposit` SET docstatus = 0 WHERE name = '{}' """.format(row['customer_deposit']),debug=1)
		frappe.db.commit()
		frappe.db.sql("""UPDATE `tabCustomer Deposit` SET tutupan = {0} WHERE name = '{1}' """.format(row['tutupan'],row['customer_deposit']),debug=1)
		# cd.tutupan = row['tutupan']
		cd.flags.ignore_permissions = True
		cd.save()
		cd.submit()

	print(str(list_gp))
	return list_gp

@frappe.whitelist()
def query_arik():
	query = frappe.db.sql("""
		SELECT
		*
		FROM
		(
		SELECT
		C.employee_name AS EmployeeName,
		'Total Pcs' AS type,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 1,A.total_pcs,0))) AS January,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 2,A.total_pcs,0))) AS February,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 3,A.total_pcs,0))) AS March,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 4,A.total_pcs,0))) AS April,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 5,A.total_pcs,0))) AS May,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 6,A.total_pcs,0))) AS June,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 7,A.total_pcs,0))) AS July,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 8,A.total_pcs,0))) AS August,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 9,A.total_pcs,0))) AS September,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 10,A.total_pcs,0))) AS October,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 11,A.total_pcs,0))) AS November,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 12,A.total_pcs,0))) AS December
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		JOIN (
		SELECT
		A.employee_name,
		B.spko
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		WHERE
		A.operation = 'Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		) C ON B.spko = C.spko
		WHERE
		A.operation = 'QC Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		GROUP BY
		C.employee_name

		UNION

		SELECT
		C.employee_name,
		'Total Ok' AS type,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 1,A.total_pcs - A.total_rusak,0))) AS January,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 2,A.total_pcs - A.total_rusak,0))) AS February,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 3,A.total_pcs - A.total_rusak,0))) AS March,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 4,A.total_pcs - A.total_rusak,0))) AS April,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 5,A.total_pcs - A.total_rusak,0))) AS May,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 6,A.total_pcs - A.total_rusak,0))) AS June,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 7,A.total_pcs - A.total_rusak,0))) AS July,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 8,A.total_pcs - A.total_rusak,0))) AS August,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 9,A.total_pcs - A.total_rusak,0))) AS September,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 10,A.total_pcs - A.total_rusak,0))) AS October,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 11,A.total_pcs - A.total_rusak,0))) AS November,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 12,A.total_pcs - A.total_rusak,0))) AS December
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		JOIN (
		SELECT
		A.employee_name,
		B.spko
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		WHERE
		A.operation = 'Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		) C ON B.spko = C.spko
		WHERE
		A.operation = 'QC Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		GROUP BY
		C.employee_name

		UNION

		SELECT
		C.employee_name,
		'Total Tidak Sesuai' AS type,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 1,A.total_rusak,0))) AS January,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 2,A.total_rusak,0))) AS February,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 3,A.total_rusak,0))) AS March,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 4,A.total_rusak,0))) AS April,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 5,A.total_rusak,0))) AS May,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 6,A.total_rusak,0))) AS June,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 7,A.total_rusak,0))) AS July,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 8,A.total_rusak,0))) AS August,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 9,A.total_rusak,0))) AS September,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 10,A.total_rusak,0))) AS October,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 11,A.total_rusak,0))) AS November,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 12,A.total_rusak,0))) AS December
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		JOIN (
		SELECT
		A.employee_name,
		B.spko
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		WHERE
		A.operation = 'Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		) C ON B.spko = C.spko
		WHERE
		A.operation = 'QC Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		GROUP BY
		C.employee_name

		UNION

		SELECT
		C.employee_name,
		D.jenis_rusak AS type,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 1,D.jumlah_rusak,0))) AS January,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 2,D.jumlah_rusak,0))) AS February,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 3,D.jumlah_rusak,0))) AS March,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 4,D.jumlah_rusak,0))) AS April,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 5,D.jumlah_rusak,0))) AS May,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 6,D.jumlah_rusak,0))) AS June,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 7,D.jumlah_rusak,0))) AS July,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 8,D.jumlah_rusak,0))) AS August,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 9,D.jumlah_rusak,0))) AS September,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 10,D.jumlah_rusak,0))) AS October,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 11,D.jumlah_rusak,0))) AS November,
		ROUND(SUM(IF(MONTH(A.waktu_selesai) = 12,D.jumlah_rusak,0))) AS December
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		JOIN (
		SELECT
		A.employee_name,
		B.spko
		FROM
		`tabWork log Testing` A
		JOIN `tabWorklog spko list` B ON A.`name` = B.parent
		WHERE
		A.operation = 'Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		) C ON B.spko = C.spko
		JOIN `tabDetail Rusak` D ON A.`name` = D.parent
		WHERE
		A.operation = 'QC Poles Manual'
		AND YEAR(A.waktu_selesai) = 2024
		AND D.jumlah_rusak > 0
		GROUP BY
		C.employee_name,
		D.jenis_rusak
						) A
	""",as_list=True,debug=1)
	return query 

@frappe.whitelist(methods = ["PUT"])
def rename_doc_tool(old, new, doctype, item_name = None, description = None, jenis = None, karet = None):
	# old = "UGGW1000108K.00000"
	# new = "UGGW.10001.08K.W.000.00.00.0"
	# doctype = "Item"
	doc = frappe.rename_doc(
		doctype,
		old,
		new,
		force=False,
		merge=False,
		ignore_permissions=False,
		ignore_if_exists=False,
		show_alert=True,
		rebuild_search=True,
	)
	if item_name:
		frappe.db.set_value(doctype, new, "item_name", item_name)
	if description:
		frappe.db.set_value(doctype, new, "description", description)
	if jenis:
		frappe.db.set_value(doctype, new, "jenis", jenis)
	if karet:
		frappe.db.set_value(doctype, new, "karet", karet)

	response = {'value':doc, 'status':200} 
	return response 