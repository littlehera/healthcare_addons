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
		{"label": "Doctor", 'width': 80, "fieldname": "doctor"},
		{"label": "Item", 'width': 80, "fieldname": "item_code"},
		{"label": "PF Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2},
		{"label": "Amount to Turnover", 'width': 150, "fieldname": "amount_to_turnover", "fieldtype":"Currency", "precision":2},
	]

	data = get_data(from_date, to_date, report_type, ref_practitioner)
	data = sorted(data, key=lambda k: k['doctor'], reverse=False)

	for row in data:
		row['posting_date'] = frappe.db.get_value("Sales Invoice",row['parent'],'posting_date')
		row['doctor'] = get_practitioner_name(row['doctor'])

	data = insert_subtotals(data,'doctor')
	data = insert_total_row(data, 'doctor')

	return columns, data

def get_data(from_date, to_date, report_type, ref_practitioner):
	return frappe.db.sql("""SELECT parent, item_code, amount, doctor, amount_to_turnover from `tabPF and Incentive Item` 
					   			where docstatus = 1 and pf_type=%s and doctor like %s""",
								(report_type,'%'+ref_practitioner+'%'), as_dict = True)

def get_practitioner_name(ref_practitioner):
	return frappe.db.get_value("Healthcare Practitioner",ref_practitioner,"practitioner_name")



def insert_subtotals(data, key_name):
	new_data = []

	total_amount = 0
	total_turnover_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount,"amount_to_turnover":total_turnover_amount})
				total_amount = 0
				total_turnover_amount = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)
		total_amount += float(row['amount'])
		total_turnover_amount += float(row['amount_to_turnover'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount, "amount_to_turnover":total_turnover_amount})
	return new_data

def insert_total_row(data, key_value):
	amount = 0
	total_turnover_amount = 0
	for row in data:
		if 'Total for' in row[key_value]:
			continue
		else:
			amount += float(row['amount'])
			total_turnover_amount += float(row['amount_to_turnover'])


	data.append({"doctor":"TOTAL", "amount":amount,"amount_to_turnover":total_turnover_amount})
	return data