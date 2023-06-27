import random

ranks = {
        'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, 
        '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
        'J': 10, 'Q': 10, 'K': 10
    }

class Card():
    def __init__(self,rank,value) -> None:
        self.Rank = rank
        self.Value = value

class Ace(Card):
    def __init__(self, rank, value) -> None:
        super().__init__(rank, value)
        self.Soft = True
    def Harden(self):
        self.Soft = False
        self.Value = 1
    
def Draw(rank=None):    
    if rank:
        if rank == 'A':
            return Ace(rank,ranks[rank]) 
        else: 
            return Card(rank,ranks[rank])
    else:
        rank, value = random.choice(list(ranks.items()))
        if rank == "A":
            return Ace(rank, value)
        else:
            return Card(rank,value)