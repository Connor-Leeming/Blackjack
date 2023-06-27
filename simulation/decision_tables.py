from json import load

def GetTables():

    def OpenRaw():
        with open('table_data.json','r') as f:
            data = load(f)
            return data
        
    def Transform(table,pkeys):
        Dkeys = list(range(2,12))

        dictionary = {}
        for i, row in enumerate(table):
            playerkey = pkeys[i]
            for j, col in enumerate(row):
                dealerkey = Dkeys[j]
                compkey = (playerkey,dealerkey)
                dictionary[compkey] = col
        
        return dictionary

    def TransformTables(raw_data,transform_function):
        
        for standhit in ["s17","h17"]:
            for tabletype in ["pair","hard","soft"]:
                data = raw_data[standhit][tabletype]
                transformed = transform_function(
                    table=data["table"],
                    pkeys=data['pkeys']
                )
                raw_data[standhit][tabletype]["table"] = transformed

        return raw_data
    
    raw = OpenRaw()
    return TransformTables(raw,Transform)