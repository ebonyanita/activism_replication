


from . import C


# built-in hook renderer(s) (called automatically by oTree)


# <hook-functions>


def content_block(player, components, **api_kwargs):
    treatment = player.participant.treatment
    
    if treatment == 'petition':
        activism_form = """
        <p>In this experiment, activism takes the form of a <b>Petition</b>.</p>
        <ul>
            <li>Signing the petition is <b>costless</b>.</li>
        </ul>
        """
    elif treatment == 'demonstration':
        activism_form = f"""
        <p>In this experiment, activism takes the form of a <b>Demonstration</b>.</p>
        <ul>
            <li>If you choose to participate, your available time for the work task will be <b>reduced by {C.DEMO_COST} seconds</b> (leaving you with {C.EFFORT_TASK_TIME - C.DEMO_COST} seconds instead of {C.EFFORT_TASK_TIME}).</li>
            <li>Your participation imposes no costs on your other group members.</li>
        </ul>
        """
    elif treatment == 'roadblock':
        activism_form = f"""
        <p>In this experiment, activism takes the form of <b>Road-blocking</b>.</p>
        <ul>
            <li>If you choose to participate, your available time for the work task will be <b>reduced by {C.ROADBLOCK_SELF_COST} seconds</b> (leaving you with {C.EFFORT_TASK_TIME - C.ROADBLOCK_SELF_COST} seconds).</li>
            <li>If at least one group member participates in road-blocking, the available time for <i>everyone else</i> in the group is <b>reduced by {C.ROADBLOCK_OTHER_COST} seconds</b>.</li>
        </ul>
        """
    
    yield f"""
    <h2>Part 2 Instructions</h2>
    
    <p>You have now completed the first part of this experiment. The second part consists of {C.NUM_ROUNDS_PART2} additional rounds.</p>

    <p>Part 2 is very similar to Part 1. You remain in the same group of four as in the first part. The difference is that <b>before</b> the work task, there is now an additional <b>Activism Stage</b>.</p>
    
    <p>As stated in the printed instructions, at the end of the experiment, the computer will randomly select one round to determine your payment. The first {C.NUM_ROUNDS_PART1} rounds, without activism, and these remaining {C.NUM_ROUNDS_PART2} rounds, with activism, are included in the draw.</p>
    
    <h3>Activism Stage</h3>
    
    <p>Before the work task begins, you will have the opportunity to participate in activism. Activism in this experiment is a public, voluntary signal of support for the cause that:</p>

    <p style="text-align: center;"><i>Everyone should contribute to the group project.</i></p>
    
    <p>At the beginning of each round, you must choose whether you want to participate (select Yes or No). Your decision will be publicly revealed to your group members during the work task.</p>
    
    {activism_form}
    
    <p>The work task and project contribution stages remain the same as before.</p>
    """
    
    yield components.next_button(label='I understand')


def meta_title_block(player, components, **api_kwargs):
    yield ""


def title_block(player, components, **api_kwargs):
    yield ""


# </hook-functions>