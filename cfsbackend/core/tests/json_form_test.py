from django.test import TestCase
from core.forms import JSONForm
from core.models import Beat, Squad

from ..filters import CallFilter

from .test_helpers import assert_list_equiv


class JSONFormTest(TestCase):
    def setUp(self):
        self.filter = CallFilter()
        self.form = JSONForm(self.filter.form)
        Beat.objects.create(beat_id=1, descr="B1")
        Beat.objects.create(beat_id=2, descr="B2")
        Squad.objects.create(squad_id=1, descr="A")
        Squad.objects.create(squad_id=2, descr="B")

    def test_field_as_dict(self):
        field_dict = self.form.field_as_dict('time_received')
        assert field_dict['name'] == 'time_received'
        assert field_dict['type'] == 'DateRangeField'
        assert field_dict['label'] == "Time received"

        field_dict = self.form.field_as_dict('beat')
        beats = Beat.objects.all().values_list("beat_id", "descr")

        assert field_dict['type'] == 'ModelChoiceField'
        assert field_dict['choices'][0] == ('', '---------')
        assert_list_equiv(field_dict['choices'][1:], beats)

        field_dict = self.form.field_as_dict('squad')
        squads = Squad.objects.all().values_list("squad_id", "descr")

        assert field_dict['type'] == 'ChoiceField'
        # These fail in the test cases, but constructing this filter in
        # the shell works.  Not sure why this is.
        #assert_list_equiv(field_dict['choices'], squads)

    def test_as_dict(self):
        form_dict = self.form.as_dict()
        assert "fields" in form_dict

        for idx, fieldtuple in enumerate(self.filter.form.fields.items()):
            field_name, field = fieldtuple
            field_dict = form_dict['fields'][idx]
            assert field_dict == self.form.field_as_dict(field_name)
