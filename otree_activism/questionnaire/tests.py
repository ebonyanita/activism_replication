from otree.api import Bot, Submission
from . import Questionnaire, FinalPayoff, ThankYou


class PlayerBot(Bot):
    def play_round(self):
        yield Questionnaire, dict(
            q1_support=True,
            q1_pressure=False,
            q1_convincing=False,
            q1_too_extreme=False,
            q1_no_earnings_effect=False,
            q1_reciprocate=False,
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
        )
        yield Submission(FinalPayoff, check_html=False)
        yield Submission(ThankYou, check_html=False)
