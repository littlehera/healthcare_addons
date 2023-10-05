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

	return columns, data
