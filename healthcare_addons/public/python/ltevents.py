import frappe

def on_save(doc, method):

    match = 0
    
    template = doc.template
    lab_template = frappe.get_doc("Lab Test Template", template)
    lab_item = lab_template.item
    si_items = frappe.get_doc("Sales Invoice", doc.custom_sales_invoice).items
    si_packed_items = frappe.get_doc("Sales Invoice", doc.custom_sales_invoice).packed_items

    for item in si_items:
        print(item.item_code, "VS", lab_item)
        if lab_item == item.item_code:
            match = 1
        print(match)
    
    if si_packed_items is not None:
        for item in si_packed_items:
            print(item.item_code, "VS", lab_item)
            if lab_item == item.item_code:
                match = 1
                print(match)
                
    if match == 0:
        frappe.throw("Lab Test Template "+template+" is not in Sales Invoice")
