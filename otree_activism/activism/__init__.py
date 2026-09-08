from otree.api import (
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    WaitPage,
    Page,
    models,
    widgets,
    Currency,
    cu,
    ExtraModel,
)
import units

doc = ''
class C(BaseConstants):
    # built-in constants
    NAME_IN_URL = 'activism'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 14
    # user-defined constants
    EFFORT_TASK_TIME = 45
    POINTS_PER_CORRECT = 10
    MPCR = 0.4
    PETITION_COST = 0
    DEMO_COST = 10
    ROADBLOCK_SELF_COST = 10
    ROADBLOCK_OTHER_COST = 5
    GRID_SIZE = 4
    MAX_ANSWER = 16
    NUM_ROUNDS_PART1 = 7
    ACTIVISM_CHOICE_TIME = 25
    CONTRIBUTE_TIME = 25
    ROUND_RESULTS_TIME = 20
    POINT_TO_EURO_RATE = 0.15
    PERCENT = 100
    GRIDS_PER_ROUND = 15
    MAX_SEAT_NUMBER = 32
    TIMER_INTERVAL_MS = 1000
    NUM_ROUNDS_PART2 = 7
    # custom columns shown in the admin Data tab
    ADMIN_VIEW_FIELDS = dict(
        group=['treatment', 'num_activists', 'num_roadblockers'],
    )
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    num_activists = models.IntegerField()
    num_roadblockers = models.IntegerField()
    treatment = models.StringField(choices=['petition', 'demonstration', 'roadblock'], label='Treatment')
    total_contribution = models.CurrencyField()
class Player(BasePlayer):
    effort_score = models.IntegerField()
    wage = models.CurrencyField()
    contribution = models.CurrencyField(label='Your contribution', min=0)
    actual_effort_time = models.IntegerField()
    chose_activism = models.BooleanField(choices=[[True, 'Yes'], [False, 'No']], label='Choose activism', widget=widgets.RadioSelect)
    round_payoff = models.CurrencyField()
    seat_number = models.IntegerField(label='Seat number', max=C.MAX_SEAT_NUMBER, min=1)
# built-in hook function(s) (called automatically by oTree)
# <hook-functions>
def creating_session(subsession: Subsession):
    import random
    if subsession.round_number == 1:
        subsession.group_randomly()
        treatments = subsession.session.config.get('treatments', ['petition', 'demonstration', 'roadblock'])
        for idx, group in enumerate(subsession.get_groups()):
            treatment = treatments[idx % len(treatments)]
            group.treatment = treatment
            for p in group.get_players():
                p.participant.treatment = treatment
    else:
        subsession.group_like_round(1)
        for group in subsession.get_groups():
            group.treatment = group.get_players()[0].participant.treatment
    for p in subsession.get_players():
        if subsession.round_number <= C.NUM_ROUNDS_PART1:
            p.actual_effort_time = C.EFFORT_TASK_TIME
    # pre-generate fixed grids for this round
    for existing in RoundGrid.filter(subsession=subsession):
        existing.delete()
    for i in range(C.GRIDS_PER_ROUND):
        grid = generate_grid(C.GRID_SIZE)
        num_ones = sum(1 for c in grid if c == '1')
        RoundGrid.create(
            subsession=subsession,
            round_number=subsession.round_number,
            trial_index=i,
            grid=grid,
            num_ones=num_ones,
        )
# </hook-functions>
# the below function(s) are user-defined, not called by oTree
# <helper-functions>
def generate_grid(size):
    import random
    rows = []
    for _ in range(size):
        row = ''.join(str(random.randint(0, 1)) for _ in range(size))
        rows.append(row)
    return '\n'.join(rows)
def soft_timer_html(time_seconds, message):
    yield f"""
    <div class="soft-timer-container" data-soft-timer="{time_seconds}" data-interval-ms="{C.TIMER_INTERVAL_MS}">
        <span class="soft-timer-countdown">Time left on this page: <span class="soft-timer-time"></span> seconds</span>
        <span class="soft-timer-message">{message}</span>
    </div>
    """
def activism_update_text(player):
    # core "X out of N group members joined activism" sentence, Part 2 only.
    # returns '' in Part 1 so callers can use it unconditionally.
    if player.round_number <= C.NUM_ROUNDS_PART1:
        return ''
    ACTION_PAST = dict(
        petition='signed the petition',
        demonstration='joined the demonstration',
        roadblock='joined the road blockade',
    )
    past = ACTION_PAST[player.participant.treatment]
    num_activists = player.group.num_activists
    if num_activists == C.PLAYERS_PER_GROUP:
        suffix = ''
    elif player.chose_activism:
        suffix = ' (including you)'
    else:
        suffix = ' (not including you)'
    return f'{num_activists} out of {C.PLAYERS_PER_GROUP} group members {past}{suffix}.'
def activism_update_html(player):
    # EffortTask version: an "Activism update:" paragraph (empty in Part 1).
    text = activism_update_text(player)
    return f'<p><b>Activism update:</b> {text}</p>' if text else ''
def round_header_text(player):
    # "Part 1 – Round X of 7" header; the round counter resets each part.
    if player.round_number <= C.NUM_ROUNDS_PART1:
        part = 1
        round_in_part = player.round_number
        total = C.NUM_ROUNDS_PART1
    else:
        part = 2
        round_in_part = player.round_number - C.NUM_ROUNDS_PART1
        total = C.NUM_ROUNDS_PART2
    return f'Part {part} – Round {round_in_part} of {total}'
def round_header_html(player):
    return f'<p class="round-header"><b>{round_header_text(player)}</b></p>'
# </helper-functions>
class RoundGrid(ExtraModel):
    subsession = models.Link(Subsession)
    round_number = models.IntegerField()
    trial_index = models.IntegerField()
    grid = models.StringField()
    num_ones = models.IntegerField()
class CountingTrial(ExtraModel):
    player = models.Link(Player)
    grid = models.StringField()
    num_ones = models.IntegerField()
    answer = models.IntegerField()
    is_correct = models.BooleanField()
class SeatNumber(Page):
    form_model = 'player'
    form_fields = ['seat_number']
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(seat_number=1), button_label='Seat 1')]
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.label = str(player.seat_number)

class WaitForSeats(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class InstructionsPart2(Page):
    form_model = 'player'
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='I confirm')]
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS_PART1 + 1
class ActivismChoice(Page):
    form_model = 'player'
    form_fields = ['chose_activism']
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [
            dict(fields=dict(chose_activism=True), button_label='Participate'),
            dict(fields=dict(chose_activism=False), button_label='Do not participate'),
        ]
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.NUM_ROUNDS_PART1
class WaitForActivism(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > C.NUM_ROUNDS_PART1
    @staticmethod
    def after_all_players_arrive(group: Group):
        num_roadblockers = sum(
            1 for p in group.get_players()
            if p.chose_activism and p.participant.treatment == 'roadblock'
        )
        group.num_roadblockers = num_roadblockers
        group.num_activists = sum(1 for p in group.get_players() if p.chose_activism)
        for p in group.get_players():
            treatment = p.participant.treatment
            chose = p.chose_activism
            if treatment == 'petition':
                p.actual_effort_time = C.EFFORT_TASK_TIME - (C.PETITION_COST if chose else 0)
            elif treatment == 'demonstration':
                p.actual_effort_time = C.EFFORT_TASK_TIME - (C.DEMO_COST if chose else 0)
            elif treatment == 'roadblock':
                if chose:
                    time_loss = C.ROADBLOCK_SELF_COST
                else:
                    time_loss = C.ROADBLOCK_OTHER_COST if num_roadblockers > 0 else 0
                p.actual_effort_time = max(0, C.EFFORT_TASK_TIME - time_loss)
class EffortTask(Page):
    timer_text = 'Time remaining:'
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='Submit')]
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        trials = CountingTrial.filter(player=player)
        correct = sum(1 for t in trials if t.is_correct)
        player.effort_score = correct
        player.wage = cu(correct * C.POINTS_PER_CORRECT)
    @staticmethod
    def get_timeout_seconds(player: Player):
        return player.actual_effort_time
    @staticmethod
    async def live_method(player: Player, data):

        # Guard against malformed/stray payloads. The client only ever sends
        # {answer, grid} (effort_task.js), but a reconnect or stray message, or
        # a non-numeric value, would otherwise raise KeyError/ValueError and
        # crash the async handler -> H13 (connection closed without response).
        if not isinstance(data, dict) or 'answer' not in data or 'grid' not in data:
            return
        try:
            answer = int(data['answer'])
        except (TypeError, ValueError):
            return
        grid_str = data['grid']
        num_ones = sum(1 for c in grid_str if c == '1')
        is_correct = answer == num_ones
        
        existing_trials = CountingTrial.filter(player=player)

        # Guard: a live message can arrive before the first trial exists
        # (reconnecting websocket, stray/duplicate message). Without this,
        # existing_trials[-1] raises IndexError and crashes the async handler,
        # which surfaces as an H13 (connection closed without response).
        if not existing_trials:
            return

        # Update the last created trial with the answer
        last_trial = existing_trials[-1]
        last_trial.answer = answer
        last_trial.is_correct = is_correct
        
        # Get the next grid
        trial_index = len(existing_trials) - 1
        next_trial_index = trial_index + 1
        grids = RoundGrid.filter(
            subsession=player.subsession, trial_index=next_trial_index
        )
        
        if grids:
            next_grid = grids[0]
            CountingTrial.create(
                player=player,
                grid=next_grid.grid,
                num_ones=next_grid.num_ones,
            )
            yield {player.id_in_group: dict(
                type='next_trial',
                grid=next_grid.grid,
                last_correct=is_correct,
            )}
        else:
            yield {player.id_in_group: dict(type='done')}
        
    @staticmethod
    def bot_mid_page(player: Player, case):
        pass
class Contribute(Page):
    form_model = 'player'
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [
            dict(fields=dict(contribution=0), button_label='Contribute 0'),
            dict(fields=dict(contribution=cu(C.POINTS_PER_CORRECT)), button_label='Contribute 10'),
        ]
    @staticmethod
    def get_form_fields(player: Player):
        return ['contribution']
    @staticmethod
    def error_message(player: Player, values):
        contribution = values['contribution']
        if float(contribution) != int(float(contribution)):
            return 'Please enter a whole number (no decimals).'
        if contribution > player.wage:
            return f'Your contribution cannot exceed your wage of {int(float(player.wage))}.'
class WaitForResults(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.total_contribution = sum((p.contribution for p in group.get_players()), cu(0))
        for p in group.get_players():
            p.round_payoff = p.wage - p.contribution + cu(round(C.MPCR * float(group.total_contribution), 2))
        if group.round_number == C.NUM_ROUNDS:
            import random
            rate = C.POINT_TO_EURO_RATE
            selected_round = random.randint(1, C.NUM_ROUNDS)
            for p in group.get_players():
                selected = p.in_round(selected_round)
                p.participant.selected_round = selected_round
                p.participant.payoff = selected.round_payoff * rate
class RoundResults(Page):
    form_model = 'player'
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='Next')]
class Conclusion(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS
    @staticmethod
    def bot_available_submissions(id_in_group, round_number, session_config):
        return [dict(fields=dict(), button_label='Continue')]
page_sequence = [SeatNumber, WaitForSeats, InstructionsPart2, ActivismChoice, WaitForActivism, EffortTask, Contribute, WaitForResults, RoundResults, Conclusion]