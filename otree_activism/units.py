from otree.api import DecimalUnit
class USD(DecimalUnit):
    input_places = 2
    input_unit_label = '€'
    currency_code = 'EUR'
    storage_places = 2
    output_min_places = 0
    output_max_places = 2
    display_min_places = 0
    display_max_places = 2