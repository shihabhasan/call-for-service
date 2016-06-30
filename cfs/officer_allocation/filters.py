from . import models
from core.filters import create_filterset

OfficerActivityFilterSet = create_filterset(
    models.OfficerActivity,
    [
        {"name": "call_unit", "rel": "CallUnit"},
        {"name": "call_unit__beat", "label": "Beat", "rel": "Beat"},
        {"name": "call_unit__district", "label": "District", "rel": "District"},
        {"name": "time", "type": "daterange"},
        {"name": "call_unit__squad", "label": "Squad", "rel": "Squad"},
    ]
)
