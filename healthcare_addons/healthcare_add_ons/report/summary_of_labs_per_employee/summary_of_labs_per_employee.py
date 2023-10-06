# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee =  filters.get("employee") if filters.get("employee") is not None else ""

	columns = [
		{"label": "Employee", 'width': 150, "fieldname": "employee_name"},
		{"label": "Patient ID", 'width': 150, "fieldname": "patient"},
		{"label": "Patient Name", 'width': 150, "fieldname": "patient_name"},
		{"label": "Total Benefit Amount", 'width': 200, "fieldname": "amount", "fieldtype":"Currency", "precision":2}	
	]

	data = frappe.db.sql("""SELECT si.custom_employee, si.patient, si.patient_name,  sum(pmt.amount) as amount from `tabSales Invoice` si join `tabInvoice Payment Table` pmt
					  		on pmt.parent = si.name where si.posting_date >= %s and si.posting_date<=%s and si.docstatus = 1 and
					  		si.custom_employee like %s and pmt.payment_mode = 'Employee Benefit' group by si.custom_employee""",
							(from_date, to_date, '%'+employee+'%'), as_dict=True)
	
	for row in data:
		row['employee_name'] = frappe.db.get_value("Employee", row['custom_employee'], 'employee_name')

	data = insert_subtotals(data, 'employee_name')
	data = insert_total_row(data, 'employee_name')

	return columns, data


def insert_subtotals(data, key_name):
	new_data = []

	total_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount})
				total_amount = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)
		total_amount += float(row['amount'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount})
	return new_data


def insert_total_row(data, key_value):
	amount = 0 
	for row in data:
		if 'Total for' in row[key_value]:
			continue
		else:
				amount += float(row['amount'])
	data.append({key_value:"TOTAL", "amount":amount})
	return data