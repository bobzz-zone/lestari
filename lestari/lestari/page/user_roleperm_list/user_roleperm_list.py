# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import *
import json

@frappe.whitelist()
def contoh_report():
    list_user = frappe.db.sql("""
        SELECT
            r.parent AS users,
            r.role,
            dp.doctype,
            dp.select,
            dp.create,
            dp.read,
            dp.write,
            dp.submit,
            dp.cancel,
            dp.export,
            dp.import,
            dp.report,
            ""
        FROM
        `tabHas Role` r
        JOIN
            (
            SELECT
            `role`,
            `parent` AS doctype,
            `select`,
                `create`,
                `read`,
                `write`,
                `submit`,
                `cancel`,
                `export`,
                `import`,
                `report`,
                ""
            FROM
                `tabDocPerm`
            UNION
            SELECT
                `role`,
                `parent` AS doctype,
                `select`,
                `create`,
                `read`,
                `write`,
                `submit`,
                `cancel`,
                `export`,
                `import`,
                `report`,
                ""
                FROM
                    `tabCustom DocPerm` ) dp
                ON dp.role = r.role
    """,as_dict=1)
    usrperm = []
    no = 0
    for row in list_user:
        no+=1
        baris_baris = {
            'no' : no,
            'user' : row['users'],
            'role' : row['role'],
            'doctype' : row['doctype'],
            'select' : row['select'],
            'create' : row['create'],
            'read' : row['read'],
            'write' : row['write'],
            'submit' : row['submit'],
            'cancel' : row['cancel'],
            'export' : row['export'],
            'import' : row['import'],
            'report' : row['report']
        }
        usrperm.append(baris_baris)
    # frappe.msgprint(str(usrperm))  
    return usrperm   