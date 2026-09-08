
from otree.api import cu

from . import C, soft_timer_html, round_header_html


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    group = player.group
    total_contrib = sum((p.contribution for p in group.get_players()), cu(0))
    wage_int = int(float(player.wage))
    contrib_int = int(float(player.contribution))
    yield f"""
    <p><b>Results:</b></p>
    <p>Your wage: {wage_int} points</p>
    <p>Your contribution: {contrib_int} points</p>
    <p>Total group contribution: {int(float(total_contrib))} points</p>
    <p>Your round payoff: {player.round_payoff} points</p>
    """
    yield from soft_timer_html(C.ROUND_RESULTS_TIME, 'Please continue.')
    yield components.next_button()
    yield components.js_script('soft_timer.js')


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield round_header_html(player)


# </hook-functions>