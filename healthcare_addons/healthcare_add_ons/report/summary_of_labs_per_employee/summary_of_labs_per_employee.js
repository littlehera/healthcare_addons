// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of Labs per Employee"] = {
	"filters": [
		{
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
		{
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "reqd": 1
        },
		{
			"fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
			"options": "Employee",
            "reqd": 0	
		}
	],
    "formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if(!(typeof data["employee_name"]=="undefined"))
             if (data["employee_name"].includes('Total')||data["employee_name"].includes('TOTAL')){
                value = '<b>'+value+'</b>'
             }
		return value
	}
};
