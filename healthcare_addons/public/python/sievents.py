# Copyright (c) 2023, littlehera and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list


def fill_pick_list(doc, method):
    items = doc.items
    pick_list = []
    doc.packed_items = []
    make_packing_list(doc)

def get_product_bundle(item):
    return frappe.db.sql("""SELECT item_code,qty,uom from `tabProduct Bundle Item` where parent =%s""",item, as_dict = True)