from otree.api import models
import units
PARTICIPANT_FIELDS = dict(
    selected_round = models.IntegerField(),
    treatment = models.StringField(choices=['petition', 'demonstration', 'roadblock']),
)
SESSION_FIELDS = dict(
    num_roadblockers = models.IntegerField(),
    treatment = models.StringField(choices=['petition', 'demonstration', 'roadblock']),
)