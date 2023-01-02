from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.dashboard.item_dashboard import get_data
from extraesia.item import get_item_available_qty


def validate_items_stock_level(doc,method):
    settings = frappe.get_single("Extraesia Settings")
    if not settings.calculate_item_stock_level:
        return
    for item in doc.items:
        item_data = get_data(item.item_code)
        for data in item_data:
            if data["warehouse"] == item.warehouse:
                if get_item_available_qty(item.item_code) < item.qty:
                    frappe.throw(_("Available for item {0} in warehouse {1} quantity {2} available for sale".format(item.item_code,item.warehouse,data["projected_qty"])))