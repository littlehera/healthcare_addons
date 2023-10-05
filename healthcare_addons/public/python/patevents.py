import frappe, datetime

def on_save(doc, method):
    lastname = doc.last_name
    firstname = doc.first_name
    middlein = doc.middle_name[0] if (doc.middle_name is not None and doc.middle_name != "") else None
    birthdate = datetime.datetime.strptime(doc.dob,"%Y-%m-%d")
    patient_name = lastname + ", "+ firstname

    if middlein is not None:
        patient_name = patient_name + " " + middlein+ "."
    
    doc.patient_name = patient_name
 
    doc.patient_id = lastname[0]+firstname[0]+str(birthdate.month).zfill(2)+str(birthdate.day).zfill(2)+str(birthdate.year)
    try:
        if doc.__islocal:
            doc.name = doc.patient_id
    except:
        pass
