import json


class JSONForm(object):
    def __init__(self, form, *args, **kwargs):
        self.form = form
        self.field_names = list(self.form.fields.keys())

    def field_as_dict(self, field_name):
        bf = self.form[field_name]
        fdict = {
            "name": field_name,
            "type": bf.field.__class__.__name__,
            "label": bf.label,
        }
        if getattr(bf.field, 'choices', None):
            fdict["choices"] = list(bf.field.choices)

        return fdict

    def as_dict(self):
        """
        Returns form as a dictionary that looks like the following:

        {
            'fields': [
                {
                    'name': name,
                    'type': type,
                    'label': label,
                    'value': value, # optional
                    'choices': [choice, choice] # if applicable
                }
            ]
        }
        """

        form_dict = {"fields": []}

        for field_name in self.field_names:
            form_dict['fields'].append(self.field_as_dict(field_name))

        return form_dict

    def as_json(self):
        return json.dumps(self.as_dict())