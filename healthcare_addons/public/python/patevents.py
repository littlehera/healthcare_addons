import frappe, datetime

def on_save(doc, method):
    lastname = doc.last_name
    firstname = doc.first_name
    birthdate = datetime.datetime.strptime(doc.dob,"%Y-%m-%d")

    doc.patient_id = lastname[0]+firstname[0]+str(birthdate.month).zfill(2)+str(birthdate.day).zfill(2)+str(birthdate.year)
    try:
        if doc.__islocal:
            doc.name = doc.patient_id
    except:
        pass
