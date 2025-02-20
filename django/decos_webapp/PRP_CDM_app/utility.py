from pathlib import Path
import json

def initChoices():
    path = Path(__file__).parent / "choices.json"
    with path.open() as f:
        d = json.load(f)            
        return d
    
choices = initChoices()

def tupleConvert(shortList):
    outlist = []
    for item in shortList:
        outlist.append((item[0],item[1]))
    return outlist