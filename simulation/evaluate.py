from deck import Ace

def Evaluate(hand):
    
    status = hand.Status
    ncards = len(hand.Cards)
    newcard = hand.Cards[-1]
    naces = sum([1 for card in hand.Cards if isinstance(card,Ace)])
    
    total = hand.Total + newcard.Value

    if ncards == 1:
        status = "soft" if isinstance(newcard,Ace) else "hard"
    
    elif ncards == 2:
        if total == 21:
            status = "blackjack"
        elif naces == 0:
            status = "hard"
        elif naces == 1:
            status = "soft"
        elif naces == 2:
            status = "soft"
            hand.Cards[1].Harden()
            total -= 10
    
    else: #More than 2 cards
        
        bust = True if total > 21 else False
        
        if isinstance(newcard,Ace):
            status = "soft"
        
        if bust:
            if (status == "soft"):
                for ace in [card for card in hand.Cards if isinstance(card,Ace)]:
                    if ace.Soft:
                        ace.Harden()
                        total -=10
                        break
                if not any([card.Soft for card in hand.Cards if isinstance(card,Ace)]):
                    status = "hard"
            else:
                status = "bust"
    
    # test pair
    def get_pair(hand):
        ranks = [card.Rank for card in hand.Cards]
        if ((ncards == 2) and (ranks[0] == ranks[1])):
            return ranks[0]
        else:
            return None


        
    return (total, status, get_pair(hand),ncards)
