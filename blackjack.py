import random
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3 as sql
import numpy as np
import matplotlib.pyplot as plt

def reset_db():

    # -------- GLOBALS -----------------------------

    # simulation parameters
    shoe_size = 0 # 0 for infinite deck
    nrounds = 10_000
    round_block_size = 100

    # decision tables
    def decision_table_constructor():
        '''
        returns a dictionary of boolean dataframes:
        {
            'split':df, (indexed by possible pairs)
            's_double':df, (rest indexed by hand sum 1-21)
            'h_double:df,
            's_hit:df,
            'h_hit:df,
        }
            (if all lookups return false then stand)

        lookup by decision_dfs['s_double'][upcard_value].iloc[player_sum]
        for split: decision_dfs['split'][upcard_value].iloc[card_value[0]]
        '''
        ranks =  [2,3,4,5,6,7,8,9,10,'A']
        pairs = [2,3,4,6,7,8,9,'A']
        split_dict = {
            # upcard : player pair
            2:[p for p in pairs if p != 4],
            3:[p for p in pairs if p != 4],
            4:pairs,
            5:pairs,
            6:pairs,
            7:[p for p in pairs if p not in [4,9]],
            8:[3,7,8,9,'A'],
            9:[8,9,'A'],
            10:[8,'A'],
            'A':[8,'A']
        }
        soft_double_dict = {
            # upcard : soft total
            2:[17],
            3:[17,18],
            4:list(range(13,19)),
            5:list(range(13,19)),
            6:list(range(13,20)),
            7:[],
            8:[],
            9:[],
            10:[],
            'A':[] 
        }
        def make_hard_double_dict():
            a = list(range(9,12))
            b = list(range(8,12))
            c = list(range(10,12))
            d = [11]
            dd = {i:a if i in [2,3,4,7] else b for i in ranks}
            dd[8],dd[9] = c,c
            dd[10],dd['A'] = d,d
            return dd
        hard_double_dict = make_hard_double_dict()

        hard_hit_dict = {
            2:[5,6,7,8,12],
            3:[5,6,7,8,12],
            4:[5,6,7,8],
            5:[5,6,7],
            6:[5,6,7],
            7:[5,6,7,8,12,13,14,15,16],
            8:[5,6,7,8,9,12,13,14,15,16],
            9:[5,6,7,8,9,12,13,14,15,16],
            10:[5,6,7,8,9,10,12,13,14,15,16],
            'A':[5,6,7,8,9,10,12,13,14,15,16],
        }

        def make_soft_hit_dict():
            a = list(range(13,18))
            b = list(range(13,19))
            return {i:a if i not in [9,10] else b for i in ranks}
        soft_hit_dict = make_soft_hit_dict()

        def make_split_df(split_dict):
            upcards = split_dict.keys()
            df = pd.DataFrame(index=upcards)
            for up in upcards:
                splits = split_dict[up]
                df[up] = [True if x in splits else False for x in upcards]
            return df
        def make_df(dd):
            upcards = dd.keys()
            df = pd.DataFrame(index=list(range(1,22)))
            for up in upcards:
                df[up] = [True if x in dd[up] else False for x in df.index]
            return df

        dfs = {
            'split':make_split_df(split_dict),
            's_double':make_df(soft_double_dict),
            'h_double':make_df(hard_double_dict),
            's_hit':make_df(soft_hit_dict),
            'h_hit':make_df(hard_hit_dict)
        }

        return dfs
    decision_tables = decision_table_constructor()
    def lookup(table,total,upcard):
        '''
        returns bool
        lookup (action,hand total,upcard) in decision table
        does not work with split
        '''
        return decision_tables[table][upcard].loc[total]

    # hand evaluators
    def upcard_value(upcard):
        '''
        convert dealer upcard rank to value
        '''
        return 10 if upcard in ['J','Q','K'] else upcard
    def raw_card_values(cards):
        '''
        returns card values array()
        couns all aces as 11

        '''
        vals = []
        for c in cards:
            if isinstance(c,int):
                vals.append(c)
            elif c in ['J','Q','K']:
                vals.append(10)
            else:
                vals.append(11)
        return vals
    def process_values(raw_values):
        '''
        can set aces to 1
        any ace still acting as 11 after this func hand == soft
        '''
        if 11 not in raw_values:
            return raw_values
        else:
            if sum(raw_values) < 22:
                return raw_values
            else:
                new_values = raw_values
                while 11 in new_values:
                    new_values[new_values.index(11)] = 1
                    if sum(new_values) < 22:
                        break
                    else:
                        continue
                return new_values
    def to_draw(cards):
        '''
        returns bool
        if card draw is needed
        '''
        return True if len(cards) < 2 else False
    def to_blackjack(cards):
        '''
        tests hand for blackjack
        '''
        return True if all(
            [
                (len(cards)==2),
                ('A' in cards),
                any(
                    [True for x in cards if x in [10,'J','Q','K']]
                )
            ]
        ) else False
    def to_bust(cards):
        '''
        return true if bust else false
        handles aces
        '''
        raw_values = raw_card_values(cards)
        
        if sum(raw_values) < 22:
            return False
        else:
            pv = process_values(raw_values)
            if sum(pv) < 22:
                return False
            else:
                return True
    def to_split(cards,upcard):         
        '''
        returns bool
        check if hand splits against upcard
        '''
        c = [card if card not in ['J','Q','K'] else 10 for card in cards]
        u = upcard_value(upcard)
        split =  True if all(
            [
                len(c) == 2,
                c[0] == c[1],
                # if upcard:pair is true in decision table
                decision_tables['split'][u].loc[c[0]]
            ]
        ) else False
        return split
    def to_double(cards,upcard):
        '''
        returns bool
        check if hand doubles against upcard
        '''
        if len(cards) != 2:
            return False
        else:
            up = upcard_value(upcard)
            total = sum(raw_card_values(cards))
            if 'A' in cards:
                return lookup('s_double',total,up)
            else:
                return lookup('h_double',total,up)
    def to_hit(cards,upcard):
        '''
        returns bool
        check if hand hits against upcard
        '''
        up = upcard_value(upcard)
        values = process_values(raw_card_values(cards))
        # is hard or soft
        if 'A' not in cards:
            state = 'hard'
        else:
            # has ace, so must have an 11 or 1

            # if any ace is acting as 11, soft
            state = 'soft' if 11 in values else 'hard'
        if state == 'soft':
            return lookup('s_hit',sum(values),up)
        elif state == 'hard':
            return lookup('h_hit',sum(values),up)
        else:
            return -1
    def winner(hand,dealer):
        if hand.busted:
            return 'lose' if not dealer.busted else 'push'
        elif hand.blackjacked:
            return 'blackjack' if not dealer.blackjacked else 'push'
        elif hand.stood:
            if dealer.busted:
                return 'win'
            else:
                p_score = hand.stood_on
                d_score = dealer.total
                if p_score == d_score:
                    return 'push'
                elif p_score > d_score:
                    return 'win'
                else:
                    return 'lose'
    def set_delta(hand,dealer):
        result = winner(hand,dealer)
        bet = hand.current_bet
        if result == 'win':
            hand.delta = bet
        elif result == 'push':
            hand.delta = 0
        elif result == 'blackjack':
            hand.delta = 1.5*bet
        else:
            hand.delta = -bet

    # deck
    def make_deck(shoe_size):
        '''
        returns deck generator
        '''
        if shoe_size == 0:
            c = None
            while True:
                yield c
                c = random.choice(
                    list(range(2,11)) + ['A','Q','K','J']
                )
        # something that makes deck generators from shoe size 
        else:
            pass   
    deck = make_deck(shoe_size)
    if shoe_size == 0:
        next(deck)

    # DB setup
    conn = sql.connect('test.db')
    cursor = conn.cursor()
    headers = [
        'round_num', 
        'hand_num', 
        'blackjack', 
        'win', 
        'push', 
        'double', 
        'bust', 
        'bust_on', 
        'stand', 
        'stand_on', 
        'split', 
        'upcard', 
        'd_bust', 
        'd_blackjack', 
        'd_stand', 
        'd_score',
        'first_act',
        'delta'
    ]
    cursor.execute('DROP TABLE IF EXISTS table1')
    def make_table_string():
        s = 'CREATE TABLE table1('
        for i in headers:
            s += f'{i}, '
        s = s[:-2]+')'
        return s
    table_string = make_table_string()
    cursor.execute(table_string)

    # --------- CLASSES ---------------

    class Table():
        def __init__(self):
            self.round = Round()
            self.roundnum = 0
            self.player = Player()
            self.data = []
        def new_round(self):
            self.round = Round()
        def resolve_round(self):
            # determine outcome of hands
            for hand in self.round.rsa:
                result = winner(hand,dealer)
                if result == 'win':
                    hand.win = True
                elif result == 'push':
                    hand.pushed = True
                elif result == 'blackjack':
                    hand.win == True
                
                # set delta
                set_delta(hand,dealer)

            # push record of hands to cache
            def push_hand_records_to_cache():
                #populate self.round_data from self.round
                hand_count = 0
                dealer = self.round.dealer
                for hand in self.round.rsa:
                    hand_count += 1
                    record = {}
                    record['round_num'] = self.roundnum
                    record['hand_num'] = hand_count
                    record['blackjack'] = hand.blackjacked
                    record['win'] = hand.win
                    record['push'] = hand.pushed
                    record['double'] = hand.doubled
                    record['bust'] = hand.busted
                    record['bust_on'] = hand.busted_on
                    record['stand'] = hand.stood
                    record['stand_on'] = hand.stood_on
                    record['split'] = hand.splitted
                    record['upcard'] = dealer.upcard
                    record['d_bust'] = dealer.busted
                    record['d_blackjack'] = dealer.blackjacked
                    record['d_stand'] = dealer.stood
                    record['d_score'] = dealer.total
                    record['first_act'] = hand.first_act
                    record['delta'] = hand.delta
                    
                    # hacky blackjack but lose bug correction
                    '''if all([
                        hand.blackjacked,
                        dealer.blackjacked==False
                    ]):
                        record['win'] == True
                        record['push'] == False
                    elif all([
                        hand.blackjacked,
                        dealer.blackjacked
                    ]):
                        record['win'] == False
                        record['push'] == True
                    else:
                        pass'''
                      
                    
                    self.data.append(record)
            push_hand_records_to_cache()
        def push_to_db(self):
            #push table data to db
            #reset table data
            headers_tuple = tuple(headers)
            records = []
            for rec in self.data:
                tup = tuple([rec[i] for i in headers_tuple])
                records.append(tup)
            for r in records:
                cursor.execute(
                    f'''
                    INSERT INTO table1{headers_tuple} VALUES {r}
                    '''
                )
            conn.commit()
            self.data = []

    class Round():
        def __init__(self):
            self.dealer = Dealer()
            self.hands = [Hand([])]
            self.rsa = []
        def new_hand(self):
            pass
        def end_hand(self):
            self.rsa.append(self.hands.pop())

    class Dealer():
        def __init__(self):
            self.cards = [next(deck),next(deck)]
            self.upcard = self.cards[0]
            self.blackjacked = False
            self.busted = False
            self.stood = False
            self.total = self.score()[1]
        def decide(self):
            if to_blackjack(self.cards):
                return 'blackjack' 
            elif to_bust(self.cards):
                return 'bust'
            elif self.is_stand():
                return 'stand'
            else:
                return 'hit'
        def bust(self):
            self.busted = True
            self.total = self.score()[1]
        def stand(self):
            self.stood = True
            self.total = self.score()[1]
        def hit(self):
            self.cards.append(next(deck))
            self.total = self.score()[1]
        def blackjack(self):
            self.blackjacked = True
        def score(self):
            '''
            returns (hard/soft , total)
            '''
            cards = self.cards
            vals = process_values(raw_card_values(cards))
            soft = True if 11 in vals else False
            total = sum(vals)
            return (soft,total)
        def is_stand(self):
            soft,total = self.score()
            if total > 16:
                return True
            else:
                return False
        def act(self):
            decision = self.decide()
            if decision == 'blackjack':
                self.blackjack()
            elif decision == 'stand':
                self.stand()
            elif decision == 'hit':
                self.hit()
            elif decision == 'bust':
                self.bust()

    class Player():
        def __init__(self):
            pass
        def decide(self,cards,upcard):
            '''
            calls global hand evaluators on current hand cards and upcard
            returns first True (order of tests matter)
            '''
            c,u = cards,upcard
            if to_draw(c):
                return 'draw'
            elif to_blackjack(c):
                return 'blackjack'
            elif to_bust(c):
                return 'bust'
            elif to_split(c,u):
                return 'split'
            elif to_double(c,u):
                return 'double'
            elif to_hit(c,u):
                return 'hit'
            else:
                return 'stand'

    class Hand():
        def __init__(self,cards=[],bet=1):
            self.cards = cards
            self.doubled = False
            self.complete = False
            self.current_bet = bet
            self.busted = False
            self.busted_on = 0
            self.stood = False
            self.stood_on = 0
            self.soft = False
            self.blackjacked = False
            self.win = False
            self.pushed = False
            self.splitted = False
            self.first_act = None
            self.delta = 0
        def act(self,decision):
            if decision == 'blackjack':
                self.blackjack()
            elif decision == 'draw':
                self.draw()
            elif decision == 'hit':
                self.hit()  
            elif decision == 'bust':
                self.bust()
            elif decision == 'stand':
                self.stand()
            elif decision == 'double':
                self.double()
            elif decision == 'split':
                self.split()    
        def draw(self):
            self.cards.append(next(deck))
        def hit(self):
            if len(self.cards) == 2 and not self.splitted:
                self.first_act = 'hit'
            self.cards.append(next(deck))
        def double(self):
            self.cards.append(next(deck))
            self.doubled = True
            self.current_bet *= 2
            self.complete = True
            score = self.score()
            self.stood_on = score[1]
            self.stood = True
            if not self.splitted:
                self.first_act = 'double'
        def bust(self):
            self.complete = True
            self.busted = True
            self.busted_on = self.score()[1]
        def stand(self):
            self.complete = True
            self.stood = True
            score = self.score()
            self.soft = score[0]
            self.stood_on = score[1]
            if len(self.cards) == 2 and not self.splitted:
                self.first_act = 'stand'   
        def blackjack(self):
            self.complete = True
            self.blackjacked = True
            if not self.splitted:
                self.first_act = 'blackjack'
        def score(self):
            '''
            returns (hard/soft , total)
            '''
            cards = self.cards
            vals = process_values(raw_card_values(cards))
            soft = True if 11 in vals else False
            total = sum(vals)
            return (soft,total)
        def split(self):
            pair = self.cards[0]
            table.round.hands.insert(-1,Hand([pair]))
            del self.cards[0]
            self.splitted = True
            self.first_act = 'split'


    #---------- BEGIN -----------------
    table = Table()
    player = table.player
    for i in range(nrounds):
        table.roundnum += 1
        table.new_round()
        round = table.round
        upcard = round.dealer.upcard

        # While players_turn: (while uncompleted hands exist)
        while len(table.round.hands) != 0:
            
            # Select top hand
            hand = round.hands[-1]

            # until the hand is set to complete
            while hand.complete == False:
                
                decision = player.decide(hand.cards,upcard)
                hand.act(decision)

            # end hand
            round.end_hand()
        
        # When all hands ended, go to dealer turn
        dealer = round.dealer
        while not any([
            dealer.busted,
            dealer.stood,
            dealer.blackjacked
        ]):
            dealer.act()
        
        table.resolve_round()
        if table.roundnum % round_block_size == 0:
            table.push_to_db()

# Helper Functions
def read_db():
    # set table to df
    conn = sql.connect('test.db')
    cur = conn.cursor
    df = pd.read_sql_query('''
        SELECT * FROM table1
    ''',conn)
    conn.close()
    
    return df

def get_delta_coeffs(df):
    '''
    parameters:
        db as pandas dataframe
    returns:
        numpy array of len 10_000
    
    returns the delta column and
    merge multi-hand rounds into one value
    '''
    return df.groupby('round_num')['delta'].sum()

def set_ruin(arr,w):
    '''
    Parameters:
        array-like
    
    sets everything after the first invalid to that
    where invalid is x<w
    if there are no invalids, return the array
    
    returns:
        np array
    '''
    arr = list(arr)
    valid = [True if x > w else False for x in arr]
    try:
        ind = valid.index(False)
    except ValueError:
        return arr
    return np.array(
        arr[:ind] + [arr[ind] for x in arr[ind:]]
    )
    
def transform(arr,b,w):
    '''
    takes delta array, transforms according to sim params
    calls set_ruin()

    Parameters:
        delta array
        b = bankroll
        w = bet size (wager)

    returns:
        transformed delta array (np array)
    '''

    return set_ruin(
        (arr*w).cumsum()+b,
        w
    )

def plot_sim(b,w,n):
    '''
    plots 9 simulations of bankroll, given b and w for n rounds
    where:
        n = number of rounds
        b = starting bankroll
        w = bet_size (wager)
    '''
    # Set figure
    fig,axs = plt.subplots(3,3,sharex=True,sharey=True,figsize=(12,7))
    
    # x values
    x = list(range(n+1)) # extra 1 because start is b at round 0
    
    # y values
    ys = []
    for i in range(9):
        # Reset db
        reset_db()
        # Read db to memory
        df = read_db()
        # Take the delta coeff column
        delta_coeffs = get_delta_coeffs(df)
        # Transform, subset to correct len
        y = transform(delta_coeffs,b,w)[:n]
        # Prepend starting balance
        y = np.insert(y,0,b,axis=0)
        # Append
        ys.append(y)
    
    # Loop through subplots
    i = 0
    for row in axs:
        for ax in row:
            delta_line, = ax.plot(x,ys[i])
            start_line, = ax.plot(x,[b for i in x],color='y')
            ruin_line, = ax.plot(x,[0 for i in x],color='r')
            ax.grid(visible=True, which='major', axis='y')
            i+=1
    
    # Super plot appearance
    fig.suptitle(f'Bankroll = {b}      Bet size = {w}      Rounds = {n}')
    start_line.set_label('Starting balance')
    ruin_line.set_label('Ruin')
    delta_line.set_label('Balance')
    fig.legend(loc='upper center',ncol=3,bbox_to_anchor=(0.5, 0.95, 0, 0))
    fig.supylabel('Balance',x=0.06)
    fig.supxlabel('Round number')

def plot_stats(df):
    fig, ax = plt.subplots(2, 2, figsize=(10,8))
    act_names = ['hit', 'stand', 'double', 'blackjack', 'split']


    # Plot 1: Hand Outcome pie ----------------------------------------------------------------


    l,w,p = df[['win','push']].value_counts().values
    outcome_labels = ['Win','Lose','Push']
    outcomes = [x * (1/sum([w,l,p])*100) for x in [w,l,p]]
    outcome_colours = ['g','r','y']
    a = ax[0][0]
    a.pie(
        outcomes,
        labels=outcome_labels,
        colors=outcome_colours,
        wedgeprops={'alpha':0.75},
        radius=1.2,
        labeldistance=None,
        autopct=lambda x: str(round(x,2))+'%'
    )
    a.set_title('Hand Outcome')
    a.legend(loc='upper left')
    a.set_facecolor('xkcd:really light blue')


    # Plot 2: First Player Action ----------------------------------------------


    acts = df.first_act.value_counts()
    act_labels,act_values = acts.index,acts.values
    act_values = [x * (1/sum(act_values)*100) for x in act_values]
    labels = [x.title() for x in act_labels]
    values = act_values
    a = ax[0][1]
    a.bar(labels,act_values)
    a.set_title('First Player Action')
    a.set_ylabel('Percent of hands')
    a.set_facecolor('xkcd:really light blue')


    #Plot 3: Dealer scores -----------------------------------------------------------


    dscores = df.d_score.value_counts().sort_index()
    x = dscores.index
    y = [
        round(
            (x/sum(dscores.values))*100,
            2
        )
        for x in dscores.values
    ]
    colours = ['b' if i < 22 else 'r' for i in x]
    ax[1][0].barh(
        x,
        y,
        color=colours,
        alpha=0.7
    )
    a = ax[1][0]
    a.set_yticks(range(x.min(),x.max()+1))
    a.set_xlabel('Percent of hands')
    a.set_ylabel('Dealer score')
    a.set_title('Dealer Score')

    # Get mu
    xs = [i for i in range(min(x),max(x)+1)]
    weights = list(dscores/sum(dscores)) 
    mu = sum([
        xs[i]*weights[i] for i in range(len(xs))
    ])

    # Plot mu line
    a.set_facecolor('xkcd:really light blue')
    ticks = range(20)
    l = a.scatter(
        ticks,
        [mu for x in ticks],
        color='y',
        marker='_',
        linewidths=3
    )
    a.legend(
        labels=['Bust','Mean'],
        handles=[
            a.get_children()[8],
            a.get_children()[10]
        ]
    )


    #Plot 4: Outcome given first action ------------------------------------------------------------


    # Hacky bugfix: some player bj showing as lost hand
    def hacky_bug_fix_1(x):
        p = True if x.blackjack == True else False
        d = True if x.d_blackjack == True else False
        if p:
            return 1 if not d else 0
        else:
            return x.win
    df['win'] = df.apply(hacky_bug_fix_1,axis=1)

    # Derive outcome column
    def map_outcome(x):
        if x['win'] == 1:
            return 'win'
        elif x['push'] == 1:
            return 'push'
        else:
            return 'lose'
    df['outcome'] = df.apply(map_outcome,axis=1)

    # Create conditional probability distributions for outcomes given act

    # Make conditional dataframe
    cond = pd.DataFrame(df.groupby('first_act').outcome.value_counts())
    cond['count'] = cond['outcome']
    cond.drop(['outcome'],axis=1,inplace=True)
    totals = cond.groupby('first_act').sum()
    cond['total'] = cond.apply(lambda x: totals.loc[x.name[0]].values[0],axis=1)
    cond['p'] = cond['count'] / cond['total']

    # Insert blackjack lose record
    cond = pd.concat(
        [
            cond,
            pd.DataFrame(
                {
                    'count':0,
                    'total':0,
                    'p':0
                },
                index=[('blackjack','lose')]
            )
        ]
    )

    # Plot
    a = ax[1][1]
    cond = cond.sort_values(['first_act','outcome'])

    # Get act name list ordered by 
    act_names = list(
        cond[cond.index.get_level_values(1)=='win'].sort_values('p',ascending=False).index.get_level_values(0)
    )

    def get_ps():
        '''    A function which extracts ordered proportions in a 2d list, ordered by highset win p:
        [[wins],[pushes],[loses]]'''
        def get_outcome_array(cond,act_names,oc):
            return [
                cond.loc[act_name].loc[oc].p *100 for act_name in act_names
            ]
        return [
            get_outcome_array(cond,act_names,x) for x in ['win','push','lose']
        ]
    p_arr = get_ps()

    # Make array of bottom coords for stacking bars
    n = len(act_names)
    bottoms = [
        [0 for i in range(n)],
        [i for i in p_arr[0]],
        [p_arr[0][i] + p_arr[1][i] for i in range(n)]
    ]

    # Plot
    a = ax[1][1]
    colours = [list(x*5) for x in ['g','y','r']]
    for i in range(3):
        ps = p_arr[i]
        bot = bottoms[i]
        a.bar(
            [x.title() for x in act_names],
            ps,
            bottom=bot,
            color=colours[i],
            alpha=0.75,
            width=0.6
        )
    a.set_title('Hand Outcome By First Action')
    a.legend(
        handles=[a.get_children()[x]for x in [0,6,11]],
        labels=['Win','Push','Lose'],
        loc='upper center',
        ncol=3,
        framealpha=1,
    )
    a.set_xlabel('First action')
    a.set_facecolor('xkcd:really light blue')
    a.set_yticks([])
