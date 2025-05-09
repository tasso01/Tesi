"""
Modulo per la raccolta dei risultati ottenuti da strumenti di analisi strutturale
in un file CSV riepilogativo.
"""
import os
import csv
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
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
    """
    Genera l'output finale in base al tool selezionato e salva i risultati in formato CSV.
    """
    tool = get_tool()
    match tool:
        case "fr3d":
            output_generator("fr3d")
        case "barnaba":
            output_generator("barnaba")
        case "rnaview":
            output_generator("rnaview")
    save_csv()

def output_generator(tool):
    """
    Elabora i file BPSEQ e TXT generati da un tool e li prepara per l'esportazione in CSV.

    Args:
        tool (str): Nome del tool per cui generare l'output.
    """
    bpseq_folder = f"output\\{tool}_bpseq"
    txt_folder = f"output\\{tool}_txt"
    for filename in os.listdir(bpseq_folder):
        bpseq_path = os.path.join(bpseq_folder, filename)
        pdb_id = os.path.splitext(filename)[0]
        pdb = pdb_id.split('_')[0]
        chain = pdb_id.split('_')[1].split('-')[0]
        txt_path = ""
        for file in os.listdir(txt_folder):
            pdb_id2 = os.path.splitext(file)[0]
            if pdb_id == pdb_id2:
                txt_path = os.path.join(txt_folder, file)
        add_pdb_id(pdb)
        add_chain(chain)
        if get_polymer_type():
            add_molecule(molecule_from_polymer(pdb, chain))
        add_bpseq_output(bpseq_path)
        add_txt_output(txt_path)
    output_number = len(os.listdir(bpseq_folder))
    insert_from_init(output_number)
    insert_non_canonical(tool)

def insert_non_canonical(tool):
    """
    Inserisce nei dati finali le strutture che contengono solo interazioni non canoniche.

    Args:
        tool (str): Nome del tool usato.
    """
    bpseq_folder = f"output\\{tool}_bpseq"
    txt_folder = f"output\\{tool}_txt"
    non_canonical = []
    bpseq_files = {
        os.path.splitext(f)[0]
        for f in os.listdir(bpseq_folder)
    }
    for f in os.listdir(txt_folder):
        base_name = os.path.splitext(f)[0]
        if base_name not in bpseq_files:
            non_canonical.append(f)
    for file in non_canonical:
        txt_path = os.path.join(txt_folder, file)
        pdb_id = os.path.splitext(file)[0]
        pdb = pdb_id.split('_')[0]
        chain = pdb_id.split('_')[1].split('-')[0]
        add_pdb_id(pdb)
        add_chain(chain)
        if get_polymer_type():
            add_molecule(molecule_from_polymer(pdb, chain))
        add_bpseq_output("")
        add_txt_output(txt_path)
    output_number = len(non_canonical)
    insert_from_init(output_number)

def insert_from_init(n):
    """
    Inserisce i dat iniziali impostati per `n` strutture analizzate.

    Args:
        n (int): Numero di righe di output da inizializzare.
    """
    polymer = polymer_from_molecule()
    for _ in range(n):
        add_tool(get_tool())
        if get_molecule_type():
            add_molecule(get_molecule_type())
            add_polymer(polymer)
        elif get_polymer_type():
            add_polymer(get_polymer_type())

def from_id_to_file(pdb_id):
    """
    Restituisce il percorso completo al file `.cif` corrispondente a un dato PDB ID.

    Args:
        pdb_id (str): Identificatore PDB da cercare.

    Returns:
        str or None: Percorso al file trovato, oppure `None` se non esiste corrispondenza.
    """
    for file in os.listdir("files_cif"):
        if pdb_id == os.path.splitext(file)[0]:
            return os.path.join("files_cif", file)

def molecule_from_polymer(pdb_id, chain):
    """
    Ricava la descrizione della molecola associata
    a una specifica catena all'interno di un file mmCIF.

    Args:
        pdb_id (str): Identificatore del file mmCIF (senza estensione).
        chain (str): Identificatore della catena da cercare.

    Returns:
        str or None: Descrizione della molecola, oppure `None` se non trovata.
    """
    mmcif_file = from_id_to_file(pdb_id)
    mmcif_dict = MMCIF2Dict(mmcif_file)
    entity_ids = mmcif_dict.get("_entity.id", [])
    descriptions = mmcif_dict.get("_entity.pdbx_description", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]
    if isinstance(descriptions, str):
        descriptions = [descriptions]
    entity_map = dict(zip(entity_ids, descriptions))
    return entity_map.get(str(chain), None)

def polymer_from_molecule():
    """
    Ricava il tipo di polimero associato alla prima struttura presente in `files_cif_id`.
    Se è stato specificato il tipo di molecola, di conseguenze il tipo di polimero
    sarà lo stesso per tutti gli output.

    Returns:
        str or None: Tipo di polimero associato alla catena oppure `None` se non trovato.
    """
    first_mmcif_id = os.listdir("files_cif_id")[0]
    pdb_id = os.path.splitext(first_mmcif_id)[0]
    pdb = pdb_id.split('_')[0]
    chain = pdb_id.split('_')[1]
    mmcif_file = os.path.join("files_cif", f"{pdb}.cif")
    mmcif_dict = MMCIF2Dict(mmcif_file)
    entity_ids = mmcif_dict.get("_entity_poly.entity_id", [])
    entity_types = mmcif_dict.get("_entity_poly.type", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]
    if isinstance(entity_types, str):
        entity_types = [entity_types]
    entity_map = dict(zip(entity_ids, entity_types))
    return entity_map.get(str(chain), None)

def save_csv():
    """
    Salva i dati raccolti durante l'elaborazione in un file CSV chiamato 'output.csv'.

    Il file generato contiene le seguenti colonne:
    - PDB_ID
    - POLYMER
    - MOLECULE
    - CHAIN
    - TOOL
    - CANONICAL_BASE_PAIRS
    - NON_CANONICAL_BASE_PAIRS

    Raises:
        ValueError: Se le liste non hanno tutte la stessa lunghezza.
    """
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
