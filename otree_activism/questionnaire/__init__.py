from otree.api import (
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    models,
    widgets,
    WaitPage,
    Page,
)
import units

doc = ''
class C(BaseConstants):
    # built-in constants
    NAME_IN_URL = 'questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    # user-defined constants
    SCALE_MIN = 1
    SCALE_MAX = 5
    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4
    Q5 = 5
    Q6 = 6
    Q7 = 7
    Q8 = 8
    POINT_TO_EURO_RATE = 0.15
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    pass
# Q1 "select all that apply" motivations, rendered as individual checkboxes.
# (field_name, label) — shared by the model fields, form_fields, bot, and template.
Q1_FIELDS = [
    ('q1_support', 'I wanted to support the cause'),
    ('q1_pressure', 'I felt social pressure from the activists in my group'),
    ('q1_convincing', "I found the activists' methods convincing"),
    ('q1_too_extreme', "I found the activists' methods too extreme"),
    ('q1_no_earnings_effect', 'I did not think the activism would affect my earnings'),
    ('q1_reciprocate', 'I wanted to reciprocate the effort made by activists'),
    ('q1_autonomy', 'I did not want others to tell me how to behave'),
]
class Player(BasePlayer):
    q1_support = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label='I wanted to support the cause')
    q1_pressure = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label='I felt social pressure from the activists in my group')
    q1_convincing = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label="I found the activists' methods convincing")
    q1_too_extreme = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label="I found the activists' methods too extreme")
    q1_no_earnings_effect = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label='I did not think the activism would affect my earnings')
    q1_reciprocate = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label='I wanted to reciprocate the effort made by activists')
    q1_autonomy = models.BooleanField(blank=True, widget=widgets.CheckboxInput, label='I did not want others to tell me how to behave')
    q1_motivation_other = models.StringField(blank=True, label='Other (please specify)')
    q2_activism_choice = models.StringField(choices=['Petition (0 cost to you)', 'Demonstration (Cost: -10 sec to you)', 'Road blocking (Cost: -10 sec to you; -5 sec to others)', 'None of the above'], label='Which type of activism would you choose?')
    q3_personal_cost = models.IntegerField(choices=[1, 2, 3, 4, 5], label='How costly did you find participating in activism to be?', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q4_cost_to_others = models.IntegerField(choices=[1, 2, 3, 4, 5], label='To what extent did the activism in your group affect other players?', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q5_extremity = models.IntegerField(choices=[1, 2, 3, 4, 5], label='How extreme did you find the activist behavior within your group to be?', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q6_legitimacy = models.IntegerField(choices=[1, 2, 3, 4, 5], label='To what extent do you feel the activism done by your group was justified?', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q7_social_id = models.IntegerField(choices=[1, 2, 3, 4, 5], label='How similar do you feel to activists in your group?', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q8_compassion = models.IntegerField(choices=[1, 2, 3, 4, 5], label='Compassion', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q8_sympathy = models.IntegerField(choices=[1, 2, 3, 4, 5], label='Sympathy', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
    q8_annoyance = models.IntegerField(choices=[1, 2, 3, 4, 5], label='Annoyance', max=C.SCALE_MAX, min=C.SCALE_MIN, widget=widgets.RadioSelectHorizontal)
class Questionnaire(Page):
    form_model = 'player'
    form_fields = [name for name, _ in Q1_FIELDS] + ['q1_motivation_other', 'q2_activism_choice', 'q3_personal_cost', 'q4_cost_to_others', 'q5_extremity', 'q6_legitimacy', 'q7_social_id', 'q8_compassion', 'q8_sympathy', 'q8_annoyance']
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [
                dict(
                    fields=dict(
                        q1_support=True,
                        q1_pressure=False,
                        q1_convincing=False,
                        q1_too_extreme=False,
                        q1_no_earnings_effect=False,
                        q1_reciprocate=True,
                        q1_autonomy=False,
                        q1_motivation_other='',
                        q2_activism_choice='Petition (0 cost to you)',
                        q3_personal_cost=3,
                        q4_cost_to_others=3,
                        q5_extremity=3,
                        q6_legitimacy=3,
                        q7_social_id=3,
                        q8_compassion=3,
                        q8_sympathy=3,
                        q8_annoyance=3,
                    ),
                    button_label='Submit questionnaire'
                ),
            ]
    @staticmethod
    def error_message(player: Player, values):
        q1_selected = any(values[name] for name, _ in Q1_FIELDS)
        q1_other = (values['q1_motivation_other'] or '').strip()
        if not q1_selected and not q1_other:
            return 'Please select at least one option for the first question (or specify "Other").'
    @staticmethod
    def before_next_page(player: Player, timeout_happened):

        pass

class FinalPayoff(Page):
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='Next')]
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        
        import time
        player.participant.stopped_at = time.time()
        
class ThankYou(Page):
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='Next')]
page_sequence = [Questionnaire, FinalPayoff, ThankYou]