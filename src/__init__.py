MOLECULE_FAMILY = ""

TOOLS = (
    "RNApolis Annotator",
    "FR3D",
    "bpnet",
    "baRNAba",
    "RNAView",
    "MC-Annotate"
)

SELECTED_TOOLS = set()

def set_molecule_family(family):
    global MOLECULE_FAMILY
    MOLECULE_FAMILY = family

def get_molecule_family():
    return MOLECULE_FAMILY

def add_tool(tool):
    global SELECTED_TOOLS
    SELECTED_TOOLS.add(tool)

def get_selected_tools():
    return SELECTED_TOOLS

def get_tools():
    return TOOLS
