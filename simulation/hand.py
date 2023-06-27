import deck
import evaluate

class Hand():
   
    def __init__(self,inserts=[]) -> None:
        
        self.Cards = []
        self.Total = 0
        self.Status = "" # {"hard","soft","blackjack","bust"}
        self.Splitted = False
        self.Pair = None
        self.ncards = 0
        self.Complete = False
        self.actions = []
        self.Doubled = False
        self.Outcome = ""
        
        for rank in inserts:
            self.Cards.append(deck.Draw(rank))
            self.Evaluate()
        while len(self.Cards) < 2:
            self.Cards.append(deck.Draw())
            self.Evaluate()       

    def Evaluate(self):
        self.Total,self.Status,self.Pair,self.ncards = evaluate.Evaluate(self)
        
        if self.Status == 'blackjack' : self.Blackjack()
        elif self.Status == 'bust' : self.Bust()

    def Draw(self):
        self.Cards.append(deck.Draw())
        self.Evaluate()

    def Blackjack(self):
        self.actions.append('blackjack')
        self.Complete = True
    
    def Hit(self):
        self.Draw()
        self.actions.append('hit')

    def Stand(self):
        self.actions.append('stand')
        self.Complete = True
    
    def Double(self):
        self.Draw()
        self.actions.append('double')
        self.Doubled = True
    
    def Bust(self):
        self.actions.append('bust')
        self.Complete = True