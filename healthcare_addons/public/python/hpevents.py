# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe

def create_sales_partner(doc, method):
    if doc.custom_type == "Doctor (MD)":
        if find_sales_partner(doc.practitioner_name):
            doc.custom_sales_partner = find_sales_partner(doc.practitioner_name)
        else:
            sales_partner = {
                "doctype": "Sales Partner",
                "partner_name": doc.practitioner_name,
                "territory": "All Territories",
                "commission_rate": 5
            }

            sp_doc = frappe.get_doc(sales_partner)
            sp_doc.insert();
            doc.custom_sales_partner = sp_doc.name

def find_sales_partner(sp_name):
    return frappe.db.get_value("Sales Partner",sp_name,"partner_name")