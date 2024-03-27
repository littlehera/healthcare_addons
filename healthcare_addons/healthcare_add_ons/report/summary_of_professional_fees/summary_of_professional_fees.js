// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary of Professional Fees"] = {
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
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
            "options": ['Consultation PF (by Doctor)','Reading PF (by Reader)', 'PF By Lab Test'],
            "reqd": 1
		},
		{
            "fieldname": "ref_practitioner",
            "label": __("Doctor"),
            "fieldtype": "Link",
            "options": "Healthcare Practitioner",
            "reqd": 0
        },
        {
            "fieldname": "item_code",
            "label": __("Lab Test"),
            "fieldtype": "Link",
            "options": "Item",
            "reqd": 0
        },
        {
            "fieldname": "show_totals",
            "label": __("Show Totals Only?"),
            "fieldtype": "Check",
            "reqd": 0
        }
	],
    "formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if(!(typeof data["parent"]=="undefined"))
             if (data["parent"].includes('Total')||data["parent"].includes('TOTAL')){
                value = '<b>'+value+'</b>'
             }
        if(!(typeof data["doctor"]=="undefined"))
             if (data["doctor"].includes('Total')||data["doctor"].includes('TOTAL')){
                value = '<b>'+value+'</b>'
             }
		return value
	}
};
