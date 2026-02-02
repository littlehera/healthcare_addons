# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	data = []
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	hmo = filters.get("hmo") if filters.get("hmo")is not None else ""
	report_type = filters.get("report_type")

	columns = get_columns(report_type)
	rows = get_data(from_date, to_date, report_type, hmo)

	for row in rows:
		row['items'], row['amount'] = get_items(row['sales_invoice'], report_type)
		row['ref_no'] = get_ref_no(row['sales_invoice'])
		row['card_no'] = get_card_no(row['sales_invoice'])
		row['doctor'] = get_doctor(row['sales_invoice'])

		if row['items'] != "":
			data.append(row)
	data = sorted(data, key=lambda k: k['hmo'], reverse=False)
	data = insert_subtotals(data, 'hmo')
	data = insert_total_row(data, 'hmo')

	return columns, data

def get_columns(report_type):
	columns = []

	if report_type == 'Laboratory Tests':
		columns = [
			{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
			{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
			{"label": "HMO", 'width': 150, "fieldname": "hmo"},
			{"label": "Patient Name", 'width': 150, "fieldname": "patient_name"},
			{"label": "Card #", 'width': 150, "fieldname": "card_no"},
			{"label": "Ref #", 'width': 150, "fieldname": "ref_no"},
			{"label": "Items", 'width': 150, "fieldname": "items"},
			{"label": "Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2}
		]
	else:
		columns = [
			{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
			{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
			{"label": "HMO", 'width': 150, "fieldname": "hmo"},
			{"label": "Patient Name", 'width': 150, "fieldname": "patient_name"},
			{"label": "Card #", 'width': 150, "fieldname": "card_no"},
			{"label": "Ref #", 'width': 150, "fieldname": "ref_no"},
			{"label": "Items", 'width': 150, "fieldname": "items"},
			{"label": "Doctor", 'width': 150, "fieldname": "doctor"},
			{"label": "Amount", 'width': 150, "fieldname": "amount", "fieldtype":"Currency", "precision":2}
		]
	return columns

def get_data(from_date, to_date, report_type, hmo):
	data = []
	if report_type == 'Laboratory Tests':
		if hmo == "":
			data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, si.patient, si.patient_name
									from `tabSales Invoice` si where si.posting_date >= %s and si.posting_date<=%s and
									si.docstatus = 1""",
									(from_date, to_date),as_dict = True)
		else:
			data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, si.patient, si.patient_name
									from `tabSales Invoice` si where si.posting_date >= %s and si.posting_date<=%s and
									si.docstatus = 1 and si.custom_hmo = %s""",
									(from_date, to_date, hmo),as_dict = True)
	else:
		if hmo == "":
			data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, si.patient, si.patient_name
									from `tabSales Invoice` si where si.posting_date >= %s and si.posting_date<=%s and
									si.docstatus = 1""",
									(from_date, to_date),as_dict = True)
		else:
			data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.custom_hmo as hmo, si.patient, si.patient_name
					   			from `tabSales Invoice` si where si.posting_date >= %s and si.posting_date<=%s and
					   			si.docstatus = 1 and si.custom_hmo = %s""",
								(from_date, to_date, hmo),as_dict = True)
	
	return data

def get_items(si, report_type):
	item_group = "Laboratory" if report_type == 'Laboratory Tests' else "Services"
	amount = 0
	items =""
	rows = frappe.db.sql("""SELECT item_code, amount from `tabSales Invoice Item` where item_code in (select name from `tabItem` where item_group = %s)
					   			and parent = %s""",(item_group, si))
	for i,row in enumerate(rows):
		amount += row[1]
		items += row[0]
		if len(rows)!= i+1:
			items += ', '
	return items, amount

def get_ref_no(si):
	rows = frappe.db.sql("""SELECT ref_no from `tabInvoice Payment Table` where parent = %s and payment_mode = 'Charge to HMO'""",si)

	if len(rows)>0:
		return rows[0][0]
	else:
		return ""

def get_card_no(si):
	rows = frappe.db.sql("""SELECT card_no from `tabInvoice Payment Table` where parent = %s and payment_mode = 'Charge to HMO'""",si)

	if len(rows)>0:
		return rows[0][0]
	else:
		return ""

def get_doctor(si):
	doctor = ""
	rows = frappe.db.sql("""SELECT doctor from `tabPF and Incentive Item` where parent = %s and item_code like %s""",(si,'%'+'Consultation'+'%'))
	for row in rows:
		doctor = frappe.db.get_value("Healthcare Practitioner",row[0],"practitioner_name")+", MD"
	return doctor

def insert_subtotals(data, key_name):
	new_data = []

	total_amount = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "amount":total_amount,})
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


	data.append({"sales_invoice":"TOTAL", "amount":amount})
	return data