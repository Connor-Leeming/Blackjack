from dealer import Dealer
from player import Player
from outcome import GetOutcome,OutcomeError

class Round():

    def __init__(self,config,dtables) -> None:
        self.dealer = Dealer()
        self.player = Player()
        
        self.player.Turn(
            config=config,
            upcard=self.dealer.upcard,
            dtables = dtables
            )
        
        self.dealer.Turn(
            config=config
        )

        self.SetOutcomes()

    def SetOutcomes(self):
        for hand in self.player.CompletedHands:
            hand.Outcome = GetOutcome(
                hand,
                self.dealer.hand
            )