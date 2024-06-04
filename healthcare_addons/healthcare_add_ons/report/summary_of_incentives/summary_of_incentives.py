# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	#filters: from_date, to_date, report_type,referred_by,package

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	report_type = filters.get("report_type")
	referred_by = filters.get("referred_by") if filters.get("referred_by") is not None else ""
	package = filters.get("package") if filters.get("package") is not None else ""
	totals_only = filters.get("totals_only")

	columns = get_columns(report_type,totals_only)
	data = get_data(from_date, to_date, report_type, referred_by, package,totals_only)

	key_ = 'custom_practitioner_name' if report_type == "By MD" else 'custom_external_referrer'

	#data = sorted(data, key=lambda k: k[key_], reverse=False)
	if totals_only == 1:
		data = get_totals_only(data, key_)
	else:
		data = insert_subtotals(data,key_)
	data = insert_total_row(data,key_, report_type)
	
	return columns, data

def get_columns(report_type, totals_only):
	if totals_only == 1:
		if report_type == "By MD":
			columns =[
				{"label": "Requesting Physician #", 'width': 150, "fieldname": "custom_practitioner_name", "fieldtype":"Data"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
				{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2},
				{"label": "SI", 'width': 150, "fieldname": "labs_percentage", "fieldtype":"Currency", "precision":2}
			]
		else:
			columns =[
				{"label": "External Referrer", 'width': 150, "fieldname": "custom_external_referrer", "fieldtype":"Data"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2}
			]
	else:
		if report_type == "By MD":
			# 1. Requesting Physician
			# 2. Posting Date
			# 3. Patient Name
			columns =[
				{"label": "Requesting Physician #", 'width': 150, "fieldname": "custom_practitioner_name", "fieldtype":"Data"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Patient Name", 'width': 150, "fieldname": "patient_name", "fieldtype":"Data"},
				{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Discount Amount", 'width': 150, "fieldname": "discount_amount", "fieldtype":"Currency", "precision":2},
				{"label": "Net Total", 'width': 150, "fieldname": "net_total", "fieldtype":"Currency", "precision":2},
				#{"label": "Amount Eligible for Incentive", 'width': 150, "fieldname": "amount_eligible_for_commission", "fieldtype":"Currency", "precision":2},
				{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2},
				{"label": "SI", 'width': 150, "fieldname": "labs_percentage", "fieldtype":"Currency", "precision":2}
			]
		else:
			# 1. External Referrer
			# 2. Posting Date
			# 3. Patient name
			# 4. Type of package
			# 5. Gross Total
			# 6. Incentive Amount
			columns =[
				{"label": "External Referrer", 'width': 150, "fieldname": "custom_external_referrer", "fieldtype":"Data"},
				{"label": "Posting Date", 'width': 80, "fieldname": "posting_date"},
				{"label": "Patient Name", 'width': 150, "fieldname": "patient_name", "fieldtype":"Data"},
				{"label": "Package", 'width': 150, "fieldname": "item_code", "fieldtype":"Data"},
				#{"label": "Sales Invoice #", 'width': 150, "fieldname": "sales_invoice", "fieldtype":"Link", "options":"Sales Invoice"},
				{"label": "Gross Total", 'width': 150, "fieldname": "total", "fieldtype":"Currency", "precision":2},
				{"label": "Incentive Amount", 'width': 150, "fieldname": "total_commission", "fieldtype":"Currency", "precision":2}
			]
	return columns

def get_data(from_date, to_date, report_type, referred_by = None, package = None, totals_only=None):
	data = []

	if report_type == "By MD":
		data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.ref_practitioner, si.patient_name, si.total, si.discount_amount, si.net_total, 
								si.total_commission, pf.amount as total_commission from `tabSales Invoice` si join `tabPF and Incentive Item` pf on si.name = pf.parent
					   			where si.docstatus = 1 and si.posting_date >=%s and si.posting_date <=%s and si.ref_practitioner like %s
					   			and pf.item_code = "INCENTIVE" and si.total_commission > 0
					   			order by si.ref_practitioner asc, sales_invoice asc, si.posting_date asc, si.patient_name asc""",
								(from_date, to_date, '%'+referred_by+'%'), as_dict = True)
		# data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, si.ref_practitioner, si.patient_name, si.total, si.discount_amount, si.net_total, 
		# 						si.total_commission, pf.amount as total_commission from `tabSales Invoice` si join `tabPF and Incentive Item` pf on si.name = pf.parent
		# 			   			where si.docstatus = 1 and si.posting_date >=%s and si.posting_date <=%s and si.ref_practitioner like %s and si.custom_source like %s
		# 			   			and pf.item_code = "INCENTIVE" and si.total_commission > 0
		# 			   			order by si.ref_practitioner asc, sales_invoice asc, si.posting_date asc, si.patient_name asc""",
		# 						(from_date, to_date, '%'+referred_by+'%', 'Doctor%'), as_dict = True)
		for row in data:
			row['labs_percentage'] = float(row['net_total'])*0.02
			row['custom_practitioner_name'] = get_practitioner_name(row['ref_practitioner'])
		
		data = sorted(data, key=lambda k: k['custom_practitioner_name'], reverse=False)

	else:

		if package is None or package == "":
			data = frappe.db.sql("""SELECT si.name as sales_invoice, si.posting_date, itm.external_referrer, si.patient_name, si.total, si.discount_amount, 
									si.net_total, si.total_commission, (si.net_total) as net_sales, si.amount_eligible_for_commission, itm.item_code,
									itm.amount_to_turnover from `tabSales Invoice` si join `tabPF and Incentive Item` itm on itm.parent = si.name 
									where si.docstatus = 1 and si.posting_date >=%s and si.posting_date <=%s and si.ref_practitioner like %s
									and (itm.item_code in (select new_item_code from `tabProduct Bundle` where custom_type = 'Package') or (itm.item_code ="REFERRAL"))
									order by si.custom_external_referrer asc, si.posting_date asc, si.patient_name asc, itm.item_code asc, si.total asc,
									si.amount_eligible_for_commission asc""",
									(from_date, to_date, '%'+referred_by+'%'), as_dict = True)
			for row in data:
				#row['total_commission'] = float(row['total_commission']) + float(row['amount_to_turnover'])
				row['total_commission'] = float(row['amount_to_turnover'])
				row['net_sales'] = float(row['net_sales']) - float(row['amount_to_turnover'])
				row['custom_external_referrer'] = row['external_referrer'] if row['external_referrer'] is not None else ""
		else:
			data = frappe.db.sql("""SELECT name as sales_invoice, posting_date, custom_external_referrer, patient_name, total, discount_amount, net_total, 
									total_commission, (net_total - total_commission) as net_sales, amount_eligible_for_commission
									from `tabSales Invoice` where docstatus = 1 and posting_date >=%s and posting_date <=%s and ref_practitioner like %s
									and name in (SELECT parent from `tabSales Invoice Item` where item_code like%s)""",
									(from_date, to_date, '%'+referred_by+'%', package), as_dict = True)
			for row in data:
				row['total_commission'] = float(row['total_commission']) + float(get_incentive_amount(package))
				row['net_sales'] = float(row['net_sales']) - float(get_incentive_amount(package))
				row['item_code'] = package
				row['custom_external_referrer'] = row['custom_external_referrer'] if row['custom_external_referrer'] is not None else ""
		data = sorted(data, key=lambda k: k['custom_external_referrer'], reverse=False)
	return data

def get_practitioner_name(ref_practitioner):
	fname = ""
	lname = ""
	fullname = ""

	doctor = frappe.get_doc("Healthcare Practitioner", ref_practitioner)
	fullname = str(doctor.last_name) + ", " + str(doctor.first_name)

	return fullname

def get_incentive_amount(product_bundle):
	amount = frappe.db.get_value("Product Bundle", product_bundle, "custom_incentive_amount")
	return amount if amount is not None else 0


def insert_subtotals(data, key_name):
	new_data = []

	total = 0
	discount_amount = 0
	net_total = 0
	total_commission = 0
	total_labs_perc = 0
	prev_si = ""

	data = sorted(data, key=lambda k: k[key_name], reverse=False)

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:"Total for "+str(prev_key_value), "total":total,"discount_amount":discount_amount,
					 			"net_total":net_total, "total_commission":total_commission, "labs_percentage":total_labs_perc})
				total = 0
				discount_amount = 0
				net_total = 0
				total_commission = 0
				if key_name == "custom_practitioner_name":
					total_labs_perc = 0
			prev_key_value = row[key_name]
		
		new_data.append(row)
		if prev_si == row['sales_invoice'] and key_name =="custom_external_referrer":
			discount_amount += float(row['discount_amount'])
			total_commission += float(row['total_commission'])
		else:			
			total += float(row['total'])
			discount_amount += float(row['discount_amount'])
			net_total += float(row['net_total'])
			total_commission += float(row['total_commission'])
			if key_name == "custom_practitioner_name":
						total_labs_perc += float(row['labs_percentage'])
	
	new_data.append({key_name:"Total for "+str(prev_key_value), "total":total,"discount_amount":discount_amount, 
				  "labs_percentage":total_labs_perc, "net_total":net_total, "total_commission":total_commission})
	return new_data

def insert_total_row(data, key_value, report_type):
	total = 0
	discount_amount = 0
	net_total = 0
	total_commission = 0 
	total_labs_perc = 0
	for row in data:
		if 'Total for' in row[key_value]:
			continue
		else:
			total += float(row['total'])
			discount_amount += float(row['discount_amount'])
			net_total += float(row['net_total'])
			total_commission += float(row['total_commission'])
			if report_type == "By MD":
				total_labs_perc += float(row['labs_percentage'])


	data.append({key_value:"TOTAL", "total":total,"discount_amount":discount_amount, "labs_percentage":total_labs_perc,
					 			"net_total":net_total, "total_commission":total_commission})
	return data

def get_totals_only(data, key_name):
	
	new_data = []
	total = 0
	discount_amount = 0
	net_total = 0
	total_commission = 0
	total_labs_perc = 0

	prev_key_value = None
	for row in data:
		if (prev_key_value!= row[key_name]) or (prev_key_value is None):
			if (prev_key_value is not None):
				new_data.append({key_name:str(prev_key_value), "total":total,"discount_amount":discount_amount,
					 			"net_total":net_total, "total_commission":total_commission, "labs_percentage":total_labs_perc})
				total = 0
				discount_amount = 0
				net_total = 0
				total_commission = 0
				if key_name == "custom_practitioner_name":
					total_labs_perc = 0
			prev_key_value = row[key_name]
		
		total += float(row['total'])
		discount_amount += float(row['discount_amount'])
		net_total += float(row['net_total'])
		total_commission += float(row['total_commission'])
		if key_name == "custom_practitioner_name":
					total_labs_perc += float(row['labs_percentage'])
	
	new_data.append({key_name:str(prev_key_value), "total":total,"discount_amount":discount_amount, 
				  "labs_percentage":total_labs_perc, "net_total":net_total, "total_commission":total_commission})
	return new_data


def is_package(item_code):
    is_pckg = False
    count_package = frappe.db.sql("""SELECT COUNT(*) from `tabProduct Bundle` where custom_type = 'Package' and new_item_code = %s""",item_code)
    if count_package[0][0]>0:
        is_pckg = True
    return is_pckg


def is_promo(item_code):
    is_promo = False
    count_promo = frappe.db.sql("""SELECT COUNT(*) from `tabProduct Bundle` where custom_type = 'Promo' and new_item_code = %s""",item_code)
    if count_promo[0][0]>0:
        is_promo = True
    return is_promo