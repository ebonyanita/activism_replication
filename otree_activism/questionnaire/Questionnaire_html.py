


from . import C, Q1_FIELDS


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    yield "<p>Please answer the following questions about your experience in this experiment.</p>"
    
    yield f"""<div class="question-section"><p><b>{C.Q1}.</b> Why did you respond to activism in the way that you did? <i>Select all that apply</i></p>"""
    for field_name, label in Q1_FIELDS:
        yield f"<div><label>{components.form[field_name]} {label}</label></div>"
    yield components.form_field('q1_motivation_other')
    yield "</div>"
    
    yield f"""<div class="question-section"><p><b>{C.Q2}.</b> If you had the option to engage in any of the following types of activism throughout the game, which would you choose to do?</p>"""
    yield components.form['q2_activism_choice']
    for error in components.form['q2_activism_choice'].errors:
        yield f'<div class="form-control-errors">{error}</div>'
    yield "</div>"
    
    yield from _scale_question(components, C.Q3, 'q3_personal_cost', 'How costly did you find participating in activism to be?', C.SCALE_MIN, C.SCALE_MAX, 'Not costly at all', 'Very costly')
    
    yield from _scale_question(components, C.Q4, 'q4_cost_to_others', 'To what extent did the activism in your group affect other players?', C.SCALE_MIN, C.SCALE_MAX, 'Not at all', 'A great deal')
    
    yield from _scale_question(components, C.Q5, 'q5_extremity', 'How extreme did you find the activist behavior within your group to be?', C.SCALE_MIN, C.SCALE_MAX, 'Not extreme at all', 'Very much extreme')
    
    yield from _scale_question(components, C.Q6, 'q6_legitimacy', 'To what extent do you feel the activism done by your group was justified?', C.SCALE_MIN, C.SCALE_MAX, 'Not at all', 'Completely')
    
    yield from _scale_question(components, C.Q7, 'q7_social_id', 'How similar do you feel to activists in your group?', C.SCALE_MIN, C.SCALE_MAX, 'Not at all', 'A great deal')
    
    yield f"""<div class="question-section"><p><b>{C.Q8}.</b> When thinking about the activists within your group, how much do you feel each of the following emotions?</p>"""
    yield f"<p><i>Scale: {C.SCALE_MIN} (None at all) &mdash; {C.SCALE_MAX} (A great deal)</i></p>"
    yield "<table>"
    for field_name, label in [('q8_compassion', 'Compassion'), ('q8_sympathy', 'Sympathy'), ('q8_annoyance', 'Annoyance')]:
        yield f"<tr><td style='padding-right:16px'>{label}</td><td>"
        for i in range(C.SCALE_MIN, C.SCALE_MAX + 1):
            yield f"<label style='margin-right:12px'>{getattr(components.form, field_name)[i-1]} {i}</label>"
        for error in components.form[field_name].errors:
            yield f"<div class='form-control-errors'>{error}</div>"
        yield "</td></tr>"
    yield "</table>"
    yield "</div>"
    
    yield components.next_button()


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield "Questionnaire"


# </hook-functions>


# the below function(s) are user-defined, not called by oTree


# <helper-functions>


def _scale_question(components, q_num, field_name, text, scale_min, scale_max, min_label, max_label):
    yield f"""<div class="question-section"><p><b>{q_num}.</b> {text}</p>"""
    yield f"<p><i>Scale: {scale_min} ({min_label}) — {scale_max} ({max_label})</i></p>"
    for i in range(scale_min, scale_max + 1):
        yield f"<label style='margin-right:12px'>{getattr(components.form, field_name)[i - scale_min]} {i}</label>"
    for error in components.form[field_name].errors:
        yield f'<div class="form-control-errors">{error}</div>'
    yield "</div>"


# </helper-functions>