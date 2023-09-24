# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list


def validate_si(doc, method):
    make_packing_list(doc)
    validate_payments(doc)

def validate_payments(doc):
    total = 0
    payments = doc.custom_invoice_payments
    for payment in payments:
        total += payment.amount
    
    if total != doc.net_total:
        frappe.throw("TOTAL PAYMENTS DOES NOT MATCH INVOICE NET TOTAL AMOUNT!")