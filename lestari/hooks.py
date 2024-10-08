from . import __version__ as app_version

app_name = "lestari"
app_title = "Lestari"
app_publisher = "DAS"
app_description = "For Lestari"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "digitalasiasolusindo@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/lestari/css/lestari.css"
# app_include_js = "/assets/lestari/js/lestari.js"
app_include_css = [
    			   '/assets/lestari/css/lestari.css',
    			   '/assets/lestari/css/dx.light.css',
				   '/assets/lestari/css/dx.dark.css',
                #    '/assets/lestari/css/frappe-datatable.min.css'
                   ]
app_include_js = ['/assets/lestari/js/dx.all.js',
                  '/assets/lestari/js/exceljs.min.js',
                  '/assets/lestari/js/FileSaver.min.js',
                  '/assets/lestari/js/jspdf.umd.min.js',
                  '/assets/lestari/js/jszip.min.js',
                  '/assets/lestari/js/polyfill.min.js',
                #   '/assets/lestari/js/Sortable.min.js',
                  '/assets/lestari/js/clusterize.min.js',
                #   '/assets/lestari/js/frappe-datatable.min.js',
                  '/assets/lestari/js/lestari.js']


# include js, css files in header of web template
# web_include_css = "/assets/lestari/css/lestari.css"
# web_include_js = "/assets/lestari/js/lestari.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "lestari/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Material Request" : "public/js/custom/material_request.js",
	"Stock Entry" : "public/js/custom/stock_entry.js",
	"Purchase Order" : "public/js/custom/purchase_order.js",
	"Purchase Invoice" : "public/js/custom/purchase_invoice.js"
}
doctype_list_js = {
	"Item" : "public/js/item_list.js",
	"Material Request" : "public/js/custom/material_request_list.js"
	}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "lestari.install.before_install"
# after_install = "lestari.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "lestari.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
	# "Form Berat Material Pohon": {
	# 	"on_save": "lestari.lestari.doctype.form_berat_material_pohon.form_berat_material_pohon.on_save"
	# }
	# "Proses Pohonan Lilin":{
	# 	"validate": "lestari.lestari.doctype.proses_pohona_lilin.proses_pohonan_lilin.validate"
	# }
	"Purchase Invoice":{
		"before_submit":"lestari.pinv_custom.submit",
		"before_cancel":"lestari.pinv_custom.cancel",
		"on_submit":"lestari.custom.custom_purchase_invoice.on_submit",
		"on_update_after_submit":"lestari.custom.custom_purchase_invoice.on_update_after_submit",
	},
	"Material Request":{
		"on_submit":"lestari.custom.custom_material_request.submit"
	},
	"Stock Entry":{
		"after_insert":"lestari.custom.custom_stock_entry.after_insert",
		"on_update":"lestari.custom.custom_stock_entry.on_update",
		"on_change":"lestari.custom.custom_stock_entry.on_change"
	},
	"Purchase Order":{
		"on_submit":"lestari.custom.custom_purchase_order.on_submit",
		"on_cancel":"lestari.custom.custom_purchase_order.on_cancel",
		# "before_save":"lestari.custom.custom_purchase_order.before_save",
	},
	"Purchase Receipt":{
		"on_submit":"lestari.custom.custom_purchase_receipt.on_submit",
		"on_cancel":"lestari.custom.custom_purchase_receipt.on_cancel",
	},
	"Supplier": {
		"after_insert":"lestari.custom.custom_supplier.after_insert"
	},
	"Payment Entry": {
		"after_insert":"lestari.custom.custom_payment_entry.after_insert"
	}
}
jenv = {
	'filters':[
		# 'get_all:lestari.lestari.doctype.rencana_produk_harian.rencana_produk_harian.get_all'
		'get_qrcode:lestari.generateqr.get_qrcode',
        'get_num2words:lestari.num2words.get_num2words'
	]
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		# "0/5 * * * *": [
		# 	"erpnext.manufacturing.doctype.bom_update_log.bom_update_log.resume_bom_cost_update_jobs",
		# ],
		# "0/30 * * * *": [
		# 	"erpnext.utilities.doctype.video.video.update_youtube_data",
		# ],
		# Hourly but offset by 30 minutes
		# "30 * * * *": [
		# 	"erpnext.accounts.doctype.gl_entry.gl_entry.rename_gle_sle_docs",
		# ],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"lestari.custom.custom_reorder_item.reorder_item",
		],
	},
# 	"all": [
# 		"lestari.tasks.all"
# 	],
# 	"daily": [
# 		"lestari.tasks.daily"
# 	],
# 	"hourly": [
# 		"lestari.tasks.hourly"
# 	],
# 	"weekly": [
# 		"lestari.tasks.weekly"
# 	]
# 	"monthly": [
# 		"lestari.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "lestari.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "lestari.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "lestari.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"lestari.auth.validate"
# ]

