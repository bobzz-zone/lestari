# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def get_monthly_sums(field_name):
    return ", ".join([
        f"ROUND(SUM(IF(MONTH(A.waktu_selesai) = {month}, {field_name}, 0))) AS {month_name}"
        for month, month_name in enumerate([
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ], start=1)
    ])

def get_base_query():
    return """
        SELECT
            A.employee_name,
            B.spko
        FROM
            `tabWork log Testing` A
        JOIN `tabWorklog spko list` B ON A.`name` = B.parent
        WHERE
            A.operation = 'Poles Manual'
            AND YEAR(A.waktu_selesai) = 2024
    """

def get_employee_data_subquery():
    return f"""
        ({get_base_query()})
    """

def get_main_query():
    monthly_total_pcs = get_monthly_sums('A.total_pcs')
    monthly_total_ok = get_monthly_sums('A.total_pcs - A.total_rusak')
    monthly_total_rusak = get_monthly_sums('A.total_rusak')
    monthly_detail_rusak = get_monthly_sums('D.jumlah_rusak')

    return f"""
        SELECT
            C.employee_name AS EmployeeName,
            'Total Pcs' AS type,
            {monthly_total_pcs}
        FROM
            `tabWork log Testing` A
        JOIN `tabWorklog spko list` B ON A.`name` = B.parent
        JOIN {get_employee_data_subquery()} C ON B.spko = C.spko
        WHERE
            A.operation = 'QC Poles Manual'
            AND YEAR(A.waktu_selesai) = 2024
        GROUP BY
            C.employee_name

        UNION

        SELECT
            C.employee_name,
            'Total Ok' AS type,
            {monthly_total_ok}
        FROM
            `tabWork log Testing` A
        JOIN `tabWorklog spko list` B ON A.`name` = B.parent
        JOIN {get_employee_data_subquery()} C ON B.spko = C.spko
        WHERE
            A.operation = 'QC Poles Manual'
            AND YEAR(A.waktu_selesai) = 2024
        GROUP BY
            C.employee_name

        UNION

        SELECT
            C.employee_name,
            'Total Tidak Sesuai' AS type,
            {monthly_total_rusak}
        FROM
            `tabWork log Testing` A
        JOIN `tabWorklog spko list` B ON A.`name` = B.parent
        JOIN {get_employee_data_subquery()} C ON B.spko = C.spko
        WHERE
            A.operation = 'QC Poles Manual'
            AND YEAR(A.waktu_selesai) = 2024
        GROUP BY
            C.employee_name

        UNION

        SELECT
            C.employee_name,
            D.jenis_rusak AS type,
            {monthly_detail_rusak}
        FROM
            `tabWork log Testing` A
        JOIN `tabWorklog spko list` B ON A.`name` = B.parent
        JOIN {get_employee_data_subquery()} C ON B.spko = C.spko
        JOIN `tabDetail Rusak` D ON A.`name` = D.parent
        WHERE
            A.operation = 'QC Poles Manual'
            AND YEAR(A.waktu_selesai) = 2024
            AND D.jumlah_rusak > 0
        GROUP BY
            C.employee_name,
            D.jenis_rusak
    """

def execute(filters=None):
    query = get_main_query()
    data = frappe.db.sql(query, as_dict=True,debug=1)
    columns = [
        {"label": "Employee Name", "fieldname": "EmployeeName", "fieldtype": "Data", "width": 150},
        {"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": 100},
        {"label": "January", "fieldname": "January", "fieldtype": "Float", "width": 100},
        {"label": "February", "fieldname": "February", "fieldtype": "Float", "width": 100},
        {"label": "March", "fieldname": "March", "fieldtype": "Float", "width": 100},
        {"label": "April", "fieldname": "April", "fieldtype": "Float", "width": 100},
        {"label": "May", "fieldname": "May", "fieldtype": "Float", "width": 100},
        {"label": "June", "fieldname": "June", "fieldtype": "Float", "width": 100},
        {"label": "July", "fieldname": "July", "fieldtype": "Float", "width": 100},
        {"label": "August", "fieldname": "August", "fieldtype": "Float", "width": 100},
        {"label": "September", "fieldname": "September", "fieldtype": "Float", "width": 100},
        {"label": "October", "fieldname": "October", "fieldtype": "Float", "width": 100},
        {"label": "November", "fieldname": "November", "fieldtype": "Float", "width": 100},
        {"label": "December", "fieldname": "December", "fieldtype": "Float", "width": 100},
    ]
    return columns, data