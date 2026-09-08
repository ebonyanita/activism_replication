


from . import C, soft_timer_html, activism_update_text, round_header_html


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    wage_int = int(float(player.wage))
    yield f"""
    <p>Your wage from the work task: <b>{wage_int}</b></p>
    <p>How much do you want to contribute to the group project?</p>
    """
    yield "<ul>"
    reminder = activism_update_text(player)
    if reminder:
        yield f"<li><b>Reminder:</b> {reminder}</li>"
    yield f"<li>You can contribute between 0 and {wage_int}.</li>"
    yield "</ul>"
    yield components.form_fields()
    yield from soft_timer_html(C.CONTRIBUTE_TIME, 'Please state your decision and continue.')
    yield components.next_button()
    yield components.js_script('soft_timer.js')
    yield components.js_script('clear_form.js')


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield round_header_html(player)


# </hook-functions>