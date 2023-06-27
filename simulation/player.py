from hand import Hand
import decide

class Player():
   
    def __init__(self) -> None:
        self.Hands = []
        self.CompletedHands = []
        self.Hands.append(Hand())

    def PlayHand(self,hand,config,upcard,dtables):
        
        while not hand.Complete:

            decision = decide.Decide(hand,config,upcard,dtables)

            if decision == 'split':
                hand = self.SplitHand(hand)
                continue 
            
            decision_action_map = {
                'hit' : hand.Hit,
                'stand' : hand.Stand,
                'double' : hand.Double,
            }

            decision_action_map[decision]()

        return hand     

    def SplitHand(self,hand):
        """
        creates two new hands, with rank of split pair as insert
        one is inserted to Hands, one is returned.
        """
        rank = hand.Cards[0].Rank

        # Splitee
        splittee = Hand([rank])
        splittee.Splitted = True
        self.Hands.insert(0,splittee)

        # Splitter
        splitter = Hand([rank])
        splitter.actions.append('split')
        return splitter      

    def Turn(self,config,upcard,dtables):
        
        while self.Hands:
            
            current_hand = self.Hands.pop()

            played = self.PlayHand(current_hand,config,upcard,dtables)

            self.CompletedHands.append(played)


    