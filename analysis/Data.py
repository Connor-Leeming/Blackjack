from json import load,dump
from pandas import DataFrame


def get_data(fp = "output.json"):
    with open(fp,'r') as f:
        return load(f)

def player_hands():
    """
    removes rounds and splitting dimension.
    removes dealer info
    returns a list of player hands.
    """
    data = get_data()
    all_hands = []
    for k,v in data.items():
        hands = v["player"]["CompletedHands"]
        all_hands.extend(hands)
    return all_hands


def outcome_tuples():
    """
    Reduces hands[] to outcome[] : (x,y)
    """
    def get_tup(hand):
        modifier = "None"
        status,outcome,doubled = hand["Status"],hand["Outcome"],hand["Doubled"]
        if status == 'blackjack' : modifier = "Blackjack"
        elif doubled : modifier = "Double"
        return (outcome.title(),modifier)
    
    return [get_tup(hand) for hand in player_hands()]


def dump_tups(fp='tups.json'):
    """
    writes outcome tups to csv
    """
    tups = outcome_tups()
    with open(fp,'w') as f:
        dump(tups,f)
    
    
def outcome_sample(n):
    with open("tups.json",'r') as f:
        data = load(f)[:n]
        return [(x,y) for [x,y] in data]