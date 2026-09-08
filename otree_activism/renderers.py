from pathlib import Path

from otree.api import url_of_static_file

_GLOBAL_STYLES_PATH = Path(__file__).parent / '_static' / 'global-styles.css'


def global_styles_block(*args, **kwargs):
    css = _GLOBAL_STYLES_PATH.read_text('utf8')
    yield f'''<style>
{css}
</style>'''
    yield f'''<script src="{url_of_static_file('otai-utils.js')}"></script>'''
