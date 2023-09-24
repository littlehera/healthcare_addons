// Copyright (c) 2023, littlehera and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Summary Reports"] = {
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
            "fieldname": "report_type",
            "label": __("Report Type"),
            "fieldtype": "Select",
            "options": ["With subtotals based on Source", "with Subtotal for each Form of Payment","Summary based on Referred By"],
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
