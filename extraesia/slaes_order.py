from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.dashboard.item_dashboard import get_data


def validate_items_stock_level(doc,method):
    for item in doc.items:
        item_data = get_data(item.item_code)
        for data in item_data:
            if data["warehouse"] == item.warehouse:
                if data["projected_qty"] < item.qty:
                    frappe.throw(_("Available for item {0} in warehouse {1} quantity {2} available for sale".format(item.item_code,item.warehouse,data["projected_qty"])))