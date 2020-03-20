from __future__ import unicode_literals
import frappe, json
from frappe import _
from six import string_types, StringIO
from frappe.desk import reportview

@frappe.whitelist()
def override_get_form_params():
    def get_form_params_override():
        """Stringify GET request parameters."""
        # frappe.msgprint("override_get_form_params")
        data = frappe._dict(frappe.local.form_dict)
        is_report = data.get('view') == 'Report'

        data.pop('cmd', None)
        data.pop('data', None)
        data.pop('ignore_permissions', None)
        data.pop('view', None)

        if "csrf_token" in data:
            del data["csrf_token"]

        if isinstance(data.get("filters"), string_types):
            data["filters"] = json.loads(data["filters"])
            for filter in data["filters"]:
                if filter[0] == "Item" and filter[1] == "item_group":
                    item_group =frappe.db.get_value("Item Group", filter[3], ["lft", "rgt"], as_dict=1)
                    child_item_groups = [d.name for d in frappe.get_all('Item Group',
                            filters= {'lft': ('>=', item_group.lft),'rgt': ('<=', item_group.rgt)})]
                    filter[2] = "in"
                    filter[3] = child_item_groups or filter[3]
        

        if isinstance(data.get("fields"), string_types):
            data["fields"] = json.loads(data["fields"])
        if isinstance(data.get("docstatus"), string_types):
            data["docstatus"] = json.loads(data["docstatus"])
        if isinstance(data.get("save_user_settings"), string_types):
            data["save_user_settings"] = json.loads(data["save_user_settings"])
        else:
            data["save_user_settings"] = True

        fields = data["fields"]

        for field in fields:
            key = field.split(" as ")[0]

            if key.startswith('count('): continue
            if key.startswith('sum('): continue
            if key.startswith('avg('): continue

            if "." in key:
                parenttype, fieldname = key.split(".")[0][4:-1], key.split(".")[1].strip("`")
            else:
                parenttype = data.doctype
                fieldname = field.strip("`")

            df = frappe.get_meta(parenttype).get_field(fieldname)
            
            fieldname = df.fieldname if df else None
            report_hide = df.report_hide if df else None

            # remove the field from the query if the report hide flag is set
            if report_hide and is_report:
                fields.remove(field)


        # queries must always be server side
        data.query = None
        data.strict = None

        return data
    reportview.get_form_params = get_form_params_override