"""
Modulo per la gestione delle configurazioni globali dell'applicazione.
Rende la cartella <src> un modulo Python, permettendo di importare
le variabili globali in altri moduli della cartella.
"""
MOLECULE_TYPE = ""

POLYMER_TYPE = ""

TOOL = ""

def set_molecule_type(family):
    global MOLECULE_TYPE
    MOLECULE_TYPE = family

def get_molecule_type():
    return MOLECULE_TYPE

def set_polymer_type(polymer):
    global POLYMER_TYPE
    POLYMER_TYPE = polymer

def get_polymer_type():
    return POLYMER_TYPE

def set_tool(tool):
    global TOOL
    TOOL = tool

def get_tool():
    return TOOL
