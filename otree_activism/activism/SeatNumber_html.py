


from . import C


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    yield """
    <h2>Welcome</h2>
    <p>Before we begin, please enter your seat number.</p>
    <p>Once all members of your group have entered their seat number, the work task will begin.</p>
    """
    yield components.form_fields()
    yield components.next_button(label='Continue')


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield ""


# </hook-functions>