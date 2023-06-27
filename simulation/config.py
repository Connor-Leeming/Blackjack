from json import load
def GetConfig():
    with open('config.json','r') as f:
        return load(f)