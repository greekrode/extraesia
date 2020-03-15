from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Extraesia"),
			"items": [
				{
					"type": "doctype",
					"name": "Extraesia Settings",
					"onboard": 1,
				},
				
			]
		},
		
		
	]
