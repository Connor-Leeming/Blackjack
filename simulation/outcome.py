
class OutcomeError(Exception):
    pass

def GetOutcome(phand,dhand): 
    
    p,d = phand,dhand
    
    # player bust
    if p.Status == 'bust': return 'lose'

    # player blackjack
    elif p.Status == 'blackjack':
        
        return 'push' if d.Total == 21 else 'win'

    # player stands
    elif p.actions[-1] == 'stand':

        if p.Status != 'bust' and d.Status == 'bust': return 'win'
        elif p.Total == d.Total : return 'push'
        elif p.Total > d.Total : return 'win'
        elif p.Total < d.Total : return 'lose'

    else:
        raise OutcomeError("GetOutcome did not assign outcome")