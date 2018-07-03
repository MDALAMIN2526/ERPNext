from frappe import _

def get_data():
	return {
		'heatmap': True,
		'heatmap_message': _('This is based on transactions against this Practitioner.'),
		'fieldname': 'practitioner',
		'transactions': [
			{
				'label': _('Appointments and Encounters'),
				'items': ['Patient Appointment', 'Encounter']
			},
			{
				'label': _('Lab Tests'),
 				'items': ['Lab Test']
			}
		]
	}
