import frappe
def patch():
	data=frappe.db.sql("select name from `tabGold Payment` where docstatus=1",as_list=1)
	for row in data:
		doc=frappe.get_doc("Gold Payment",row[0])
		doc.update_against()
		frappe.db.commit()
def submit(doc,method):
	#validate used full advance
	deposit=[]
	payment=[]
	gle=[]
	for row in doc.advances:
		gle.append(row.reference_row)
		if row.reference_type =="Gold Payment":
			if row.allocated_amount != row.advance_amount:
				frappe.throw("Hutang titipan supplier harus di pakai semua")
			else:
				payment.append(row.reference_name)
		elif row.reference_type =="Customer Deposit":
			if row.allocated_amount != row.advance_amount:
				frappe.throw("Hutang titipan supplier harus di pakai semua")
			else:
				deposit.append(row.reference_name)
	deposit_str= '","'.join(deposit)
	payment_str= '","'.join(payment)
	gle_str = '","'.join(gle)
	gabungan = """{}","{}""".format(deposit_str,payment_str)
	frappe.db.sql("""update `tabStock Payment` set reference_type='Purchase Invoice' , reference_name='{}' where parent in ("{}")""".format(doc.name,gabungan),as_list=1)
	frappe.db.sql("""update `tabGL Entry` set against_voucher_type="Purchase Invoice" , against_voucher="{}" where name in ("{}") """.format(doc.name,gle_str),as_list=1)
def cancel(doc,method):
	deposit=[]
	payment=[]
	gle=[]
	for row in doc.advances:
		gle.append(row.reference_row)
		if row.reference_type =="Gold Payment":
			payment.append(row.reference_name)
		elif row.reference_type =="Customer Deposit":
			deposit.append(row.reference_name)
	deposit_str= '","'.join(deposit)
	payment_str= '","'.join(payment)
	gle_str = '","'.join(gle)
	gabungan = """{}","{}""".format(deposit_str,payment_str)
	frappe.db.sql("""update `tabStock Payment` set reference_type='' , reference_name='' where parent in ("{}")""".format(gabungan),as_list=1)
	frappe.db.sql("""update `tabGL Entry` set against_voucher_type="" , against_voucher="" where name in ("{}") """.format(gle_str),as_list=1)
#	frappe.db.commit()
