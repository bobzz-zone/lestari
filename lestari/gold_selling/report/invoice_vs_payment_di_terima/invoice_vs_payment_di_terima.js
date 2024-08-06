// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Invoice VS Payment Di terima"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.month_start(),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.now_date(),
			"reqd": 1
		}
	]
};
