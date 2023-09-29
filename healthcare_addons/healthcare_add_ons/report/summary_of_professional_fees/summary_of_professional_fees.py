# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	report_type = filters.get("report_type")
	ref_practitioner = filters.get("ref_practitioner") if filters.get("ref_practitioner") is not None else ""
	
	columns =[
		{"label": "Sales Invoice #", 'width': 150, "fieldname": "parent", "fieldtype":"Link", "options":"Sales Invoice"},
		{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
		{"label": "Item", 'width': 80, "fieldname": "item_code"},
		{"label": "PF Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
		{"label": "Amount to Turnover", 'width': 150, "fieldname": "amount_to_turnover", "fieldtype":"Currency", "precision":2},
	]

	data = get_data(from_date, to_date, report_type, ref_practitioner)

	for row in data:
		row['posting_date'] = frappe.db.get_value("Sales Invoice",row['parent'],'posting_date')

	return columns, data

def get_data(from_date, to_date, report_type, ref_practitioner):
	return frappe.db.sql("""SELECT parent, item_code, amount, doctor, amount_to_turnover from `tabPF and Incentive Item` 
					   			where docstatus = 1 and pf_type=%s and doctor like %s""",
								(report_type,'%'+ref_practitioner+'%'), as_dict = True)