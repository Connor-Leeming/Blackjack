from config import GetConfig
from decision_tables import GetTables
from round import Round
from json import dump

def Simulate(nrounds,file="../analysis/output.json"):
    
    def unpack_round_data(obj):
        
        if hasattr(obj,'__dict__'):
            obj = vars(obj) 
        if isinstance(obj, dict):
            return {k: unpack_round_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [unpack_round_data(v) for v in obj]
        else:
            return obj
    
    def output(data,file):
        if file:
            with open(file,'w') as f:
                dump(data,f)
        else:
            return data
    
    Config = GetConfig()
    Decision_tables = GetTables()
    Rounds = [Round(Config, Decision_tables) for i in range(nrounds)]
    RoundsData = {i: unpack_round_data(round) for i, round in enumerate(Rounds)}
    
    return output(RoundsData,file)


s = Simulate(10000)