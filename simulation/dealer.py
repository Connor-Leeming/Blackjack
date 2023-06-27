from hand import Hand

class Dealer():
    hand = None
    upcard = None

    def __init__(self) -> None:
        self.hand = Hand()
        self.upcard = self.hand.Cards[0]

    def Turn(self,config):
        dss17 = config['dealer stands on soft 17']
        hand = self.hand

        while not hand.Complete:

            if hand.Total < 17:
                hand.Hit()
            
            elif hand.Total == 17:
                if hand.Status == 'hard':
                    hand.Stand()
                else: # if soft
                    hand.Stand() if dss17 else hand.Hit()
            
            else:

                hand.Stand()