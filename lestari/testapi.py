import frappe
import json
from frappe.utils import flt
# @frappe.whitelist()
#     response = json.loads(str(resep))
#     # response = frappe.new_doc("Resep Mul Karet")
#     # response.rubber_mould = "KCCWBMT-10003"
#     # response.final_product = "?"
#     # response.type_mul =
#     return response

def regen_gl():
#	data = frappe.db.sql("select d.parent from `tabPurchase Invoice Item` d where d.docstatus=1 and d.item_code in (select name from `tabItem` i where i.is_stock_item=1) group by d.parent",as_list=1)
#	total=len(data)
#	for row in data:
	doc = frappe.get_doc("Purchase Invoice","ACC-PINV-2024-00296")
	frappe.db.sql("delete from `tabGL Entry` where voucher_no='ACC-PINV-2024-00296' and voucher_type='Purchase Invoice' ")
	doc.make_gl_entries()
	frappe.db.commit()
#		print(total)
#		total=total-1
def fix_outstanding():
	data = frappe.db.sql("select name,grand_total from `tabGold Invoice` where docstatus=1",as_list=1)
	for row in data:
		payment = frappe.db.sql("select sum(allocated) as total from `tabGold Payment Invoice` where gold_invoice='{}' and docstatus=1 group by gold_invoice ".format(row[0]),as_list=1)
		#update
		if payment and len(payment)>0:
			frappe.db.sql("update `tabGold Invoice` set outstanding={} where name='{}'".format(flt(row[1])-flt(payment[0][0]),row[0]),as_list=1)

def fix_mr():
	frappe.db.sql("update `tabMaterial Request Item` set ordered_qty=0 where docstatus=0")
	data = frappe.db.sql("select name from `tabMaterial Request` where docstatus=1 and material_request_type='Purchase'",as_list=1)
	for row in data:
		mr = frappe.get_doc("Material Request",row[0])
		mr.update_completed_qty()
		frappe.db.commit()
def test_patch():
    list_gp = frappe.db.sql("select name from `tabGold Payment` where docstatus=1",as_list=1)
    for row in list_gp:
        no_doc=row[0]
        frappe.db.sql("delete from `tabGL Entry` where voucher_no='{}' and voucher_type='Gold Payment'".format(no_doc))
        doc = frappe.get_doc("Gold Payment", no_doc)
        doc.make_gl_entries()
        print(no_doc)
        frappe.db.commit()
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_group(doctype, txt, searchfield, start, page_len, filters=None):
    frappe.msgprint('masukpython')
    select = frappe.db.sql("""
        SELECT name, 
        item_group,
        item_name,
        item_code,
        kadar,
        qty_isi_pohon,
        weight_per_unit
        FROM `tabItem` 
        WHERE item_group IN (
            SELECT 
            name 
            FROM `tabItem Group` 
            WHERE parent_item_group IN (
                SELECT name FROM `tabItem Group` WHERE old_parent = '{}'
            )
        )		
		""".format(filters.get('item_group')), {
		# 'txt': "%{}%".format(txt),
		# '_txt': txt.replace("%", ""),
		'start': start,
		'page_len': page_len
	})
    frappe.msgprint(str(select))
    return select

@frappe.whitelist()
def item_form_order(item=None):
    item = json.loads(item)
    doc = frappe.new_doc("Form Order")
    for row in item:
        baris_baru = {
            "model" : row,
            "item_name" : frappe.db.get_value("Item",row,'item_name'),
            "kadar" : frappe.db.get_value("Item",row,'kadar'),
            "sub_kategori" : frappe.db.get_value("Item",row,'item_group'),
            "kategori" : frappe.db.get_value("Item",row,'item_group_parent'),
            "kategori_pohon" : frappe.db.get_value("Item",row,'kategori_pohon'),
            "qty_isi_pohon" : frappe.db.get_value("Item",row,'qty_isi_pohon'),
            "image" : frappe.db.get_value("Item",row,'image'),
        }
        doc.append("items",baris_baru)
    doc.flags.ignore_permissions = True
    doc.save()
    return doc.as_dict()

@frappe.whitelist()
def repair_gl_entry_malik(doctype = "Purchase Invoice",docname = "ACC-PINV-2024-00787"):
	
	docu = frappe.get_doc(doctype, docname)	
	# delete_sl = frappe.db.sql(""" DELETE FROM tabStock Ledger Entry WHERE voucher_no = "{}" """.format(docname))
	delete_gl = frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(docname))

	# frappe.db.sql(""" UPDATE tabSingles SET VALUE = 1 WHERE field = "allow_negative_stock" """)
	# docu.update_stock_ledger()
	docu.make_gl_entries()
	# frappe.db.sql(""" UPDATE tabSingles SET VALUE = 0 WHERE field = "allow_negative_stock" """)

@frappe.whitelist()
def repair_gl_entry_arif():
    doctype = "Purchase Invoice"
    docname = [
        'ACC-PINV-2024-03581',
'ACC-PINV-2024-03581',
'ACC-PINV-2024-03581',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03888',
'ACC-PINV-2024-03910',
'ACC-PINV-2024-03910',
'ACC-PINV-2024-03910',
'ACC-PINV-2024-03911',
'ACC-PINV-2024-03911',
'ACC-PINV-2024-03911',
'ACC-PINV-2024-03913',
'ACC-PINV-2024-03913-1',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03925',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03929-1',
'ACC-PINV-2024-03934',
'ACC-PINV-2024-03935',
'ACC-PINV-2024-03935',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03936-1',
'ACC-PINV-2024-03943',
'ACC-PINV-2024-03943',
'ACC-PINV-2024-03943',
'ACC-PINV-2024-03943-1',
'ACC-PINV-2024-03943-1',
'ACC-PINV-2024-03943-1'
    ]
    for row in docname:
        docu = frappe.get_doc(doctype, row)	
        # delete_sl = frappe.db.sql(""" DELETE FROM tabStock Ledger Entry WHERE voucher_no = "{}" """.format(row))
        delete_gl = frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(row))
        print('GL Deleted '+row)

        # frappe.db.sql(""" UPDATE tabSingles SET VALUE = 1 WHERE field = "allow_negative_stock" """)
        # docu.update_stock_ledger()
        docu.make_gl_entries()
        print('GL Created '+row)

        # digunakan jika backdate
        # for row in docu.items:
        # 	update_entries_after({
        # 		"item_code": row.item_code,
        # 		"warehouse": row.warehouse,
        # 		"posting_date": docu.posting_date,
        # 		"posting_time": docu.posting_time
        # 	})
        # frappe.db.sql(""" UPDATE tabSingles SET VALUE = 0 WHERE field = "allow_negative_stock" """)
