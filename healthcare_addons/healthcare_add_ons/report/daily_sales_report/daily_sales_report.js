// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Report"] = {
	"filters": [
		{
            "fieldname": "report_type",
            "label": __("Report Type"),
            "fieldtype": "Select",
            "options": ["With subtotals based on Source", "with Subtotal for each Form of Payment"],
            "reqd": 1
        },
		{
            "fieldname": "totals_only",
            "label": __("Show Totals Only?"),
            "fieldtype": "Check",
            "default":0
        }
	],
    "formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
        if(!(typeof data["custom_source"]=="undefined"))
            if (data["custom_source"].includes('Total for')||data["custom_source"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
        }
        if(!(typeof data["payment_mode"]=="undefined"))
            if (data["payment_mode"].includes('Total')||data["payment_mode"].includes('TOTAL')){
                value = '<b style="background: #ffe9a5;">'+value+'</b>'
            }
		return value
	}
};
