import os
import csv
from src import get_tool, get_molecule_type, get_polymer_type

PDB_IDS = []

POLYMERS = []

MOLECULES = []

CHAINS = []

TOOLS = []

BPSEQ_OUTPUT = []

TXT_OUTPUT = []

def add_pdb_id(pdb_id):
    PDB_IDS.append(pdb_id)

def add_polymer(polymer):
    POLYMERS.append(polymer)

def add_molecule(molecule):
    MOLECULES.append(molecule)

def add_chain(chain):
    CHAINS.append(chain)

def add_tool(tool):
    TOOLS.append(tool)

def add_bpseq_output(bpseq):
    BPSEQ_OUTPUT.append(bpseq)

def add_txt_output(txt):
    TXT_OUTPUT.append(txt)

def check_tool():
    tool = get_tool()
    match tool:
        case "FR3D":
            fr3d_output()
        case "baRNAba":
            barnaba_output()
        case "RNAView":
            rnaview_output()
    save_csv()

def fr3d_output():
    bpseq_folder = "fr3d_bpseq"
    txt_folder = "fr3d_txt"
    for filename in os.listdir(bpseq_folder):
        bpseq_path = os.path.join(bpseq_folder, filename)
        pdb_id = os.path.splitext(filename)[0]
        txt_path = ""
        for file in os.listdir(txt_folder):
            pdb_id2 = os.path.splitext(file)[0]
            if (pdb_id == pdb_id2):
                txt_path = os.path.join(txt_folder, file)
        pdb = pdb_id.split('_')[0]
        chain = pdb_id.split('_')[1].split('-')[0]
        add_pdb_id(pdb)
        add_chain(chain)
        add_bpseq_output(bpseq_path)
        add_txt_output(txt_path)
    output_number = len(os.listdir(bpseq_folder))
    insert_from_init(output_number)

def barnaba_output():
    bpseq_folder = "barnaba_bpseq"
    txt_folder = "barnaba_txt"
    for filename in os.listdir(bpseq_folder):
        bpseq_path = os.path.join(bpseq_folder, filename)
        pdb_id = os.path.splitext(filename)[0]
        txt_path = ""
        for file in os.listdir(txt_folder):
            pdb_id2 = os.path.splitext(file)[0]
            if (pdb_id == pdb_id2):
                txt_path = os.path.join(txt_folder, file)
        pdb = pdb_id.split('_')[0]
        chain = pdb_id.split('_')[1].split('-')[0]
        add_pdb_id(pdb)
        add_chain(chain)
        add_bpseq_output(bpseq_path)
        add_txt_output(txt_path)
    output_number = len(os.listdir(bpseq_folder))
    insert_from_init(output_number)

def rnaview_output():
    bpseq_folder = "rnaview_bpseq"
    txt_folder = "rnaview_txt"
    for filename in os.listdir(bpseq_folder):
        bpseq_path = os.path.join(bpseq_folder, filename)
        pdb_id = os.path.splitext(filename)[0]
        pdb = pdb_id.split('_')[0]
        txt_path = ""
        for file in os.listdir(txt_folder):
            pdb_id2 = os.path.splitext(file)[0]
            if (pdb_id == pdb_id2):
                txt_path = os.path.join(txt_folder, file)
        chain = pdb_id.split('_')[1].split('-')[0]
        add_pdb_id(pdb)
        add_chain(chain)
        add_bpseq_output(bpseq_path)
        add_txt_output(txt_path)
    output_number = len(os.listdir(bpseq_folder))
    insert_from_init(output_number)

def insert_from_init(n):
    for _ in range(n):
        add_tool(get_tool())
        if get_molecule_type():
            add_molecule(get_molecule_type())
            add_polymer("")
        elif get_polymer_type():
            add_polymer(get_polymer_type())
            add_molecule("")
        else:
            raise TypeError("Polimero o Molecola mancante")

def save_csv():
    nome_file = "output.csv"
    lunghezza = len(PDB_IDS)
    if not all(len(lst) == lunghezza for lst in [POLYMERS, MOLECULES, CHAINS, TOOLS, BPSEQ_OUTPUT, TXT_OUTPUT]):
        raise ValueError("Tutte le liste devono avere la stessa lunghezza")
    with open(nome_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["PDB_ID", "POLYMER", "MOLECULE", "CHAIN", "TOOL", "CANONICAL_BASE_PAIRS", "NON_CANONICAL_BASE_PAIRS"])
        for i in range(lunghezza):
            writer.writerow([
                PDB_IDS[i],
                POLYMERS[i],
                MOLECULES[i],
                CHAINS[i],
                TOOLS[i],
                BPSEQ_OUTPUT[i],
                TXT_OUTPUT[i]
            ])
    print(f"File '{nome_file}' salvato correttamente.")
    print("--------------------------------------------------")
