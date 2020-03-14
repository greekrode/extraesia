from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.stock.utils import get_stock_balance, get_latest_stock_qty



def set_item_balance(doc,method):
    balance = get_item_balance(doc.item_code) + doc.actual_qty
    frappe.db.set_value("Item",doc.item_code,"balance",balance)


def get_item_balance(item):
    item_balance = get_latest_stock_qty(item)
    return item_balance