from os import environ
SESSION_CONFIG_DEFAULTS = dict(participation_fee=0.0, real_world_currency_per_point=None)
SESSION_CONFIGS = [
    dict(name='activism_pet_first', num_demo_participants=8, app_sequence=['activism', 'questionnaire'], participation_fee=5.0, treatments=['petition', 'demonstration', 'roadblock'], monitor_session_fields=['num_roadblockers', 'treatment'], monitor_participant_fields=['treatment']),
    dict(name='activism_demo_first', num_demo_participants=8, app_sequence=['activism', 'questionnaire'], participation_fee=5.0, treatments=['demonstration', 'roadblock', 'petition'], monitor_session_fields=['num_roadblockers', 'treatment'], monitor_participant_fields=['treatment']),
]
LANGUAGE_CODE = 'en'
DEMO_PAGE_INTRO_HTML = ''
THOUSAND_SEPARATOR = ''
CURRENCY_UNIT = 'units.USD'
ENABLE_ADMIN_CHAT = False
ROOMS = [dict(name='test', display_name='test'), dict(name='lab_s1', display_name='lab_s1'), dict(name='lab_s2', display_name='lab_s2')]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'blahblahblah')

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

PARTICIPANT_FIELDS = ['treatment', 'selected_round', 'stopped_at']


