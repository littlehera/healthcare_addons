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
	]
};
