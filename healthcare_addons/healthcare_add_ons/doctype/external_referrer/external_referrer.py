# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document

class ExternalReferrer(Document):
	def validate(doc):
		if find_sales_partner(doc.name):
			doc.sales_partner = find_sales_partner(doc.name)
		else:
			sales_partner = {
				"doctype": "Sales Partner",
				"partner_name": doc.name,
				"territory": "All Territories",
				"commission_rate": 0
			}

			sp_doc = frappe.get_doc(sales_partner)
			sp_doc.insert();
			doc.sales_partner = sp_doc.name

def find_sales_partner(sp_name):
    return frappe.db.get_value("Sales Partner",sp_name,"partner_name")
