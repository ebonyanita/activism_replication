from otree.api import Bot, Submission
from . import C, SeatNumber, InstructionsPart2, ActivismChoice, WaitForActivism, EffortTask, Contribute, WaitForResults, RoundResults


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield SeatNumber, dict(seat_number=self.player.id_in_group)

        if self.round_number == C.NUM_ROUNDS_PART1 + 1:
            yield InstructionsPart2

        if self.round_number > C.NUM_ROUNDS_PART1:
            yield ActivismChoice, dict(chose_activism=True)

        yield Submission(EffortTask, check_html=False)
        yield Contribute, dict(contribution=0)
        yield RoundResults
