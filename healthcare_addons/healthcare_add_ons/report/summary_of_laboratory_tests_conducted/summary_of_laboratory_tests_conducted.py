# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	#columns, data = [], []

	columns = [
		{"label": "Item", 'width': 150, "fieldname": "item_name"},
		{"label": "Total Qty", 'width': 150, "fieldname": "qty"},
	]
	
	data = get_data(from_date, to_date)

	return columns, data

def get_data(from_date, to_date):
	data = []
	items = frappe.db.sql("""SELECT name, item_name from `tabItem` where item_group = 'Laboratory'""")
	for item in items:
		item_code = item[0]
		item_name = item[1]
		si_qty = get_si_item_total(from_date, to_date, item_code)
	return data

def get_si_item_total(from_date, to_date, item_code):
	qty = frappe.db.sql("""SELECT SUM(qty) from `tabSales Invoice Item` where item_code = %s and docstatus = 1""",item_code)
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0


def get_bundle_item_total(from_date, to_date, item_code):
	qty = frappe.db.sql("""SELECT SUM(qty) from `tabPacked Item` where item_code = %s and docstatus = 1""",item_code)
	if len(qty)<1:
		return 0
	else:
		return qty[0][0] if qty[0][0] is not None else 0