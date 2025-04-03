"""
Modulo per la gestione dell'importazione e della configurazione di file mmCIF.

Funzionalità principali:
- Importa file mmCIF da una cartella contenente solo file `.cif` oppure li scarica
  a partire da un file `.txt` contenente iPDB id separati da virgole.
- Imposta le variabili globali: molecola, polimero, software da utilizzare
"""
import shutil
import os
import requests
from src import set_molecule_type, set_polymer_type, set_tool

def insert_path(valid_path):
    """
    Verifica il il percorso in input è corretto:
    - cartella contenente file PDBx/mmCIF
    - file di testo contenente PDB id separati da virgola

    Args:
        valid_path (str): percorso in input.
    
    Raises:
        OSError: Se il percorso non rispetta i requisti.
    """
    if os.path.isdir(valid_path):
        if all(f.endswith('.cif') for f in os.listdir(valid_path)):
            copy_folder(valid_path)
        else:
            raise OSError("La cartella non contiene solo file mmCIF")
    elif os.path.isfile(valid_path) and valid_path.lower().endswith('.txt'):
        with open(valid_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if all(part.strip().isalnum() for part in content.split(',')):
                download_cif(valid_path)
            else:
                raise OSError("Il file di testo non contiene solo PDB_ID")
    else:
        raise OSError("Il percorso non è una cartella nè un file di testo")

def copy_folder(source_path):
    """
    Copia il contenuto di una cartella sorgente nella cartella 'files_cif'.

    Args:
        source_path (str): Percorso della cartella sorgente contenente file mmCIF.

    Raises:
        shutil.Error: Se si verifica un errore durante la copia dei file.
    """
    destination_path = "files_cif"
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)
    try:
        shutil.copytree(source_path, destination_path)
        print(f"Cartella '{destination_path}' contenente i file mmCIF importata")
        print("--------------------------------------------------")
    except shutil.Error as e:
        print(f"Errore durante la copia della cartella: {e}")

def download_cif(source_path):
    """
    Scarica file mmCIF da RCSB PDB sulla base di PDB ID presenti nel file di testo.
    I file `.cif` corrispondenti vengono scaricati nella cartella 'files_cif'.

    Args:
        source_path (str): Percorso al file `.txt` contenente i PDB ID.

    Raises:
        requests.exceptions.RequestException: Se si verifica un errore durante il download dei file.
    """
    destination_path = "files_cif"
    if os.path.exists(destination_path):
        for file_name in os.listdir(destination_path):
            file_path = os.path.join(destination_path, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_path)
    with open(source_path, "r", encoding='utf-8') as file:
        content = file.read().strip()
    pdb_ids = content.split(",")
    base_url = "https://files.rcsb.org/download/{}.cif"
    for pdb_id in pdb_ids:
        pdb_id = pdb_id.strip()
        url = base_url.format(pdb_id)
        file_path = os.path.join(destination_path, f"{pdb_id}.cif")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Scaricato {pdb_id}.cif")
        except requests.exceptions.RequestException as e:
            print(f"Errore nel download di {pdb_id}: {e}")
    print(f"Cartella '{destination_path}' contenente i file mmCIF creata")
    print("--------------------------------------------------")

def insert_family(family):
    """
    Imposta il tipo di molecola (famiglia) specificato.

    Args:
        family (str): Nome della famiglia molecolare da impostare.
    """
    set_molecule_type(family)

def insert_polymer(polymer):
    """
    Imposta il tipo di polimero in base all'argomento della pipeline.

    Args:
        polymer (str): Codice del tipo di polimero.

    Raises:
        ValueError: Se il codice non corrisponde a un tipo valido.
    """
    polymers = {
        'c': "cyclic-pseudo-peptide",
        'o': "other",
        'p': "peptide nucleic acid",
        'd': "polydeoxyribonucleotide",
        'h': "polydeoxyribonucleotide/polyribonucleotide hybrid",
        'a': "polypeptide(D)",
        'b': "polypeptide(L)",
        'r': "polyribonucleotide"
    }
    if polymer not in polymers:
        raise ValueError("Polimero non valido")
    set_polymer_type(polymers[polymer])

def insert_tool(tool):
    """
    Imposta il tool da utilizzare per l'analisi strutturale.

    Args:
        tool (str): Codice del tool da utilizzare.

    Raises:
        ValueError: Se il codice non corrisponde a un tool valido.
    """
    tools = {
        'f': "fr3d",
        'b': "barnaba",
        'r': "rnaview",
    }
    if tool not in tools:
        raise ValueError("Tool non valido")
    set_tool(tools[tool])
