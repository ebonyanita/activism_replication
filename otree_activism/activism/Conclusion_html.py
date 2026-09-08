


from . import C


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    yield """
    <p>This completes the two parts of the experiment.</p>
    <p>On the next page you will be asked to complete a short questionnaire.</p>
    <p>Your payment round will be revealed on the final page.</p>
    """
    yield components.next_button()


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield ""


# </hook-functions>
