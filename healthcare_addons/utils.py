import frappe
from healthcare_addons.public.python.sievents import cancel_si, validate_si

def revert_si(si):
    si_doc = frappe.get_doc("Sales Invoice", si)
    cancel_si(si_doc,"")
    frappe.db.sql("""UPDATE `tabSales Invoice` set docstatus = 0 where name = %s""",si)
    frappe.db.sql("""UPDATE `tabSales Invoice Item` set docstatus = 0 where parent = %s""",si)
    frappe.db.commit()
    
def submit_si(si):
    si_doc = frappe.get_doc("Sales Invoice", si)
    frappe.db.sql("""UPDATE `tabSales Invoice` set docstatus = 1 where name = %s""",si)
    frappe.db.sql("""UPDATE `tabSales Invoice Item` set docstatus = 1 where parent = %s""",si)
    frappe.db.commit()

