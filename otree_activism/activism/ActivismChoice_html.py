


from . import C, soft_timer_html, round_header_html


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    treatment = player.participant.treatment
    if treatment == 'petition':
        description = """
    <p>You have the opportunity to <b>sign a petition</b> supporting the message
    that everyone should contribute to the group project.</p>
    <p>Signing the petition is <b>costless</b>.</p>
    """
    elif treatment == 'demonstration':
        description = f"""
    <p>You have the opportunity to <b>join a demonstration</b> supporting the message
    that everyone should contribute to the group project.</p>
    <p>Joining the demonstration will cost you <b>{C.DEMO_COST} seconds</b>
    from your work task time.</p>
    """
    elif treatment == 'roadblock':
        description = f"""
    <p>You have the opportunity to <b>participate in a road blockade</b> supporting
    the message that everyone should contribute to the group project.</p>
    <p>Participating in the road blockade will cost you <b>{C.ROADBLOCK_SELF_COST} seconds</b>
    from your work task time.</p>
    <p>Additionally, if anyone in your group participates in the road blockade,
    every non-participating group member loses <b>{C.ROADBLOCK_OTHER_COST} seconds</b>
    from their work task time.</p>
    """
    else:
        description = ""
    yield f"""
    <p><b>Activism opportunity</b></p>
    {description}
    <p>Do you want to participate?</p>
    """
    yield components.form_fields()
    yield from soft_timer_html(C.ACTIVISM_CHOICE_TIME, 'Please state your decision and continue.')
    yield components.next_button()
    yield components.js_script('soft_timer.js')
    yield components.js_script('clear_form.js')


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield round_header_html(player)


# </hook-functions>