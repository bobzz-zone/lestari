from peewee import *
import time
import frappe

database = MySQLDatabase('_1bd3e0294da19198', **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '192.168.3.15', 'user': 'root', 'password': 'password'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class TabItem(BaseModel):
    _assign = TextField(null=True)
    _comments = TextField(null=True)
    _liked_by = TextField(null=True)
    _user_tags = TextField(null=True)
    allow_alternative_item = IntegerField(constraints=[SQL('DEFAULT 0')])
    asset_category = CharField(null=True)
    asset_naming_series = CharField(null=True)
    auto_create_assets = IntegerField(constraints=[SQL('DEFAULT 0')])
    available_for_stock_payment = IntegerField(constraints=[SQL('DEFAULT 0')])
    barang_yang_dibawa_sales = IntegerField(constraints=[SQL('DEFAULT 0')])
    batch_number_series = CharField(null=True)
    brand = CharField(null=True)
    country_of_origin = CharField(null=True)
    create_new_batch = IntegerField(constraints=[SQL('DEFAULT 0')])
    creation = DateTimeField(null=True)
    customer = CharField(null=True)
    customer_code = CharField(null=True)
    customs_tariff_number = CharField(null=True)
    default_bom = CharField(null=True)
    default_item_manufacturer = CharField(null=True)
    default_manufacturer_part_no = CharField(null=True)
    default_material_request_type = CharField(constraints=[SQL("DEFAULT 'Purchase'")], null=True)
    deferred_expense_account = CharField(null=True)
    deferred_revenue_account = CharField(null=True)
    delivered_by_supplier = IntegerField(constraints=[SQL('DEFAULT 0')])
    description = TextField(null=True)
    disabled = IntegerField(constraints=[SQL('DEFAULT 0')], index=True)
    docstatus = IntegerField(constraints=[SQL('DEFAULT 0')])
    enable_deferred_expense = IntegerField(constraints=[SQL('DEFAULT 0')])
    enable_deferred_revenue = IntegerField(constraints=[SQL('DEFAULT 0')])
    end_of_life = DateField(constraints=[SQL("DEFAULT '2099-12-31'")], null=True)
    gold_selling_item = CharField(null=True)
    grant_commission = IntegerField(constraints=[SQL('DEFAULT 1')])
    has_batch_no = IntegerField(constraints=[SQL('DEFAULT 0')])
    has_expiry_date = IntegerField(constraints=[SQL('DEFAULT 0')])
    has_serial_no = IntegerField(constraints=[SQL('DEFAULT 0')])
    has_variants = IntegerField(constraints=[SQL('DEFAULT 0')])
    hub_category_to_publish = CharField(null=True)
    hub_sync_id = CharField(null=True, unique=True)
    hub_warehouse = CharField(null=True)
    idcarat = IntegerField(constraints=[SQL('DEFAULT 0')])
    idproduct = IntegerField(constraints=[SQL('DEFAULT 0')], index=True)
    idx = IntegerField(constraints=[SQL('DEFAULT 0')])
    image = TextField(null=True)
    include_item_in_manufacturing = IntegerField(constraints=[SQL('DEFAULT 0')])
    inspection_required_before_delivery = IntegerField(constraints=[SQL('DEFAULT 0')])
    inspection_required_before_purchase = IntegerField(constraints=[SQL('DEFAULT 0')])
    is_customer_provided_item = IntegerField(constraints=[SQL('DEFAULT 0')])
    is_fixed_asset = IntegerField(constraints=[SQL('DEFAULT 0')])
    is_item_from_hub = IntegerField(constraints=[SQL('DEFAULT 0')])
    is_purchase_item = IntegerField(constraints=[SQL('DEFAULT 1')], index=True)
    is_sales_item = IntegerField(constraints=[SQL('DEFAULT 1')], index=True)
    is_stock_item = IntegerField(constraints=[SQL('DEFAULT 0')])
    is_sub_contracted_item = IntegerField(constraints=[SQL('DEFAULT 0')])
    item_code = CharField(null=True, unique=True)
    item_group = CharField(index=True, null=True)
    item_group_parent = CharField(index=True, null=True)
    item_name = CharField(index=True, null=True)
    item_periode = DateField(null=True)
    item_type = CharField(constraints=[SQL('DEFAULT 'Stock'')], null=True)
    jenis = CharField(null=True)
    kadar = CharField(null=True)
    karet = CharField(null=True)
    kategori_part = CharField(null=True)
    kategori_pohon = CharField(null=True)
    last_purchase_rate = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    lead_time_days = IntegerField(constraints=[SQL('DEFAULT 0')])
    max_discount = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    min_order_qty = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    modified = DateTimeField(index=True, null=True)
    modified_by = CharField(null=True)
    name = CharField(primary_key=True)
    naming_series = CharField(null=True)
    no_of_months = IntegerField(constraints=[SQL('DEFAULT 0')])
    no_of_months_exp = IntegerField(constraints=[SQL('DEFAULT 0')])
    opening_stock = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    over_billing_allowance = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    over_delivery_receipt_allowance = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    owner = CharField(null=True)
    parent = CharField(index=True, null=True)
    parentfield = CharField(null=True)
    parenttype = CharField(null=True)
    production_from = CharField(null=True)
    publish_in_hub = IntegerField(constraints=[SQL('DEFAULT 0')])
    published_in_website = IntegerField(constraints=[SQL('DEFAULT 0')])
    purchase_uom = CharField(null=True)
    qty_isi_pohon = IntegerField(constraints=[SQL('DEFAULT 0')])
    quality_inspection_template = CharField(null=True)
    retain_sample = IntegerField(constraints=[SQL('DEFAULT 0')])
    safety_stock = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    sales_uom = CharField(null=True)
    sample_quantity = IntegerField(constraints=[SQL('DEFAULT 0')])
    serial_no_series = CharField(null=True)
    shelf_life_in_days = IntegerField(constraints=[SQL('DEFAULT 0')])
    skip_mr = IntegerField(constraints=[SQL('DEFAULT 0')])
    standard_rate = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    stock_uom = CharField(null=True)
    synced_with_hub = IntegerField(constraints=[SQL('DEFAULT 0')])
    temp_account = CharField(null=True)
    total_projected_qty = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    valuation_method = CharField(null=True)
    valuation_rate = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    variant_based_on = CharField(constraints=[SQL('DEFAULT 'Item Attribute'')], null=True)
    variant_of = CharField(index=True, null=True)
    variasi_enamel = CharField(null=True)
    variasi_marking = CharField(null=True)
    variasi_putih = CharField(null=True)
    variasi_sepuh = CharField(null=True)
    variasi_size = CharField(null=True)
    variasi_slep = CharField(null=True)
    variasi_stone = CharField(null=True)
    warranty_period = CharField(null=True)
    weight_per_unit = DecimalField(constraints=[SQL('DEFAULT 0.000000000')])
    weight_uom = CharField(null=True)

    class Meta:
        table_name = 'tabItem'

class TabItemDefault(BaseModel):
    buying_cost_center = CharField(null=True)
    company = CharField(null=True)
    creation = DateTimeField(null=True)
    default_discount_account = CharField(null=True)
    default_price_list = CharField(null=True)
    default_provisional_account = CharField(null=True)
    default_supplier = CharField(null=True)
    default_target_warehouse = CharField(null=True)
    default_warehouse = CharField(null=True)
    docstatus = IntegerField(constraints=[SQL('DEFAULT 0')])
    expense_account = CharField(null=True)
    idx = IntegerField(constraints=[SQL('DEFAULT 0')])
    income_account = CharField(null=True)
    modified = DateTimeField(index=True, null=True)
    modified_by = CharField(null=True)
    name = CharField(primary_key=True)
    owner = CharField(null=True)
    parent = CharField(index=True, null=True)
    parentfield = CharField(null=True)
    parenttype = CharField(null=True)
    selling_cost_center = CharField(null=True)

    class Meta:
        table_name = 'tabItem Default'

@frappe.whitelist()
def deleteitem():
    data = ['RCAB.0.40.20K.Y.P075.1.H4.R180']

    index = 0

    for i in data:
        try:
            q = TabItem.delete().where(TabItem.name == i)
            q.execute()
            r = TabItemDefault.delete().where(TabItemDefault.parent == i)
            q.execute()
        except Exception as e:
            print(e)

    # for i in data:
    #     try:
    #         start = time.time()
    #         frappe.delete_doc('Item', i)
    #         stop = time.time()
    #         frappe.db.commit()
    #         print(stop - start, i, index+1)
    #     except:
    #         pass
    #     index+=1
