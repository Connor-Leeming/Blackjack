def Decide(hand,config,upcard,dtables):
       
    if hand.Status in ['blackjack','bust'] : return hand.Status

    def GetActionMap(config,hand):
    
        ncards = len(hand.Cards)
        splitted = True if hand.Splitted else False
        double_split = config["double after split"]    
        
        def AllowDouble(ncards,splitted,double_split):

            if ncards != 2 : return False
            
            if splitted:
                return True if double_split else False
            else:
                return True
        
        allow_double = AllowDouble(ncards,splitted,double_split)

        mapping = {}

        mapping['h'] = "hit"
        mapping['s'] = "stand"
        mapping['p'] = "split"
        mapping['Ds'] = "double" if allow_double else "stand"
        mapping['Dh'] = "double" if allow_double else "hit" 
        mapping['Ph'] = "split" if config["double after split"] else "hit"
        mapping['Rh'] = "surrender" if config["surrender"] else "hit"
        mapping['Rp'] = "surrender" if config["surrender"] else "split"
        mapping['Rs'] = "surrender" if config["surrender"] else "stand"

        return mapping
   
    
    action_map = GetActionMap(config,hand)
    dkey = upcard.Value
    
    def table_lookup():
        sh17 = 's17' if config['dealer stands on soft 17'] else 'h17'
        pair = hand.Pair
        if pair and pair in ['2','3','4','6','7','8','9','A']:
                return dtables[sh17]['pair']['table'][(pair,dkey)]
        else:
            total = hand.Total
            
            # total adjustment
            vaildpkeys = list(dtables[sh17][hand.Status]['pkeys'])
            if total < min(vaildpkeys): 
                total = min(vaildpkeys)
            elif total > max(vaildpkeys):
                total = max(vaildpkeys)

            return dtables[sh17][hand.Status]["table"][(total,dkey)]
        
    
    lookup = table_lookup()
    
    return action_map[lookup]