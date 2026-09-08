


from . import C
from activism import C as ActivismC


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    payoff = player.participant.payoff
    fee = float(player.session.config.get('participation_fee', 0))
    if payoff is not None:
        selected_round = player.participant.selected_round
        if selected_round <= ActivismC.NUM_ROUNDS_PART1:
            part = 1
            round_in_part = selected_round
        else:
            part = 2
            round_in_part = selected_round - ActivismC.NUM_ROUNDS_PART1
        payoff_eur = float(payoff)
        total_eur = payoff_eur + fee
        yield f"""
        <h2>Your Results</h2>
        <p>Round {round_in_part} of Part {part} was randomly selected for payoff. In that round, you earned €{payoff_eur:.2f}.</p>
        <p>If this experiment is randomly selected for payoff at the end of the session, your total payment will be:</p>
        <p style="text-align: center;"><b>€{total_eur:.2f} = €{payoff_eur:.2f} (round {round_in_part} of Part {part} payment) + €{fee:.2f} fixed fee</b></p>
        """
    else:
        yield "<p>Your payment will be calculated and displayed shortly.</p>"
    yield components.next_button()


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield ""


# </hook-functions>