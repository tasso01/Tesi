"""
Modulo per l'estrazione e la conversione di file mmCIF basati su tipi di molecola o polimero.

Funzionalità principali:
- Estrae record atomici da file mmCIF in base agli `entity_id`
  associati a una molecola o a un tipo di polimero specificato.
- Converte i file mmCIF filtrati in formato PDB utilizzando un eseguibile esterno (BeEM.exe).
- Utilizzo di `Bio.PDB.MMCIF2Dict` per la lettura e interpretazione dei file mmCIF.
"""
import os
import shutil
import subprocess
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src import get_molecule_type, get_polymer_type

def extract_atoms_from_ids(file_cif, entity_ids):
    """
    Estrae e salva i record atomicida un file mmCIF corrispondenti a specifici ID.
    Per ciascun `entity_id` specificato, la funzione crea un nuovo file `.cif` nella cartella
    'files_cif_id'.

    Args:
        file_cif (str): Percorso al file mmCIF da cui estrarre i dati.
        entity_ids (set[int]): Insieme di ID da cui estrarre i record atomici.
    """
    output_folder = "files_cif_id"
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    record = {entity_id: [] for entity_id in entity_ids}
    with open(file_cif, encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        if line.startswith("_atom_site."):
            for key in record:
                record[key].append(line)
        if line.startswith("ATOM"):
            chain = int(line.split()[7])
            if chain in record:
                record[chain].append(line)
    for entity_id, atoms_lines in record.items():
        output_file = os.path.join(output_folder, f"{pdb_id}_{entity_id}.cif")
        with open(output_file, "w", encoding='utf-8') as f:
            for atom in atoms_lines:
                f.write(atom)
        print(f"ATOM di {pdb_id} per entity_id {entity_id} salvati in {output_file}")

def extract_ids_from_molecule(mmcif_file, molecule):
    """
    Estrae gli ID delle entità da un file mmCIF in base al tipo di molecola specificato.

    Args:
        mmcif_file (str): Percorso al file mmCIF da elaborare.
        molecule (str): Tipo di molecola da cercare.
    """
    entity_ids = set()
    cif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = cif_dict.get("_entity.id", [])
    molecules_types = cif_dict.get("_entity.pdbx_description", [])
    for entity_id, molecule_type in zip(entity_ids_list, molecules_types):
        if molecule_type.strip() == molecule:
            entity_ids.add(int(entity_id))
    extract_atoms_from_ids(mmcif_file, entity_ids)

def extract_ids_from_polymer(mmcif_file, polymer):
    """
    Estrae gli ID delle entità da un file mmCIF in base al tipo di polimero specificato.

    Args:
        mmcif_file (str): Percorso al file mmCIF da elaborare.
        polymer (str): Tipo di polimero da cercare.
    """
    entity_ids = set()
    cif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = cif_dict.get("_entity_poly.entity_id", [])
    polymers_types = cif_dict.get("_entity_poly.type", [])
    for entity_id, polymer_type in zip(entity_ids_list, polymers_types):
        if polymer_type.strip() == polymer:
            entity_ids.add(int(entity_id))
    extract_atoms_from_ids(mmcif_file, entity_ids)

def process_all_cif_files():
    """
    Elabora tutti i file mmCIF nella cartella 'files_cif'
    per estrarre identificatori molecolari o polimerici.
    I risultati vengono salvati nella cartella 'files_cif_id'.

    La funzione sceglie il metodo di estrazione in base all'argomento impostato nella pipeline:
    - Se è stato specificato un tipo di polimero, usa `extract_ids_from_polymer`.
    - Se è stato specificato un tipo di molecola, usa `extract_ids_from_molecule`.

    Raises:
        TypeError: Se non è stato specificato né un tipo di polimero né un tipo di molecola.
    """
    cif_folder = "files_cif"
    destination_folder = "files_cif_id"
    if os.path.exists(destination_folder):
        for f in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, f)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    if get_polymer_type():
        for cif_file in os.listdir(cif_folder):
            cif_path = os.path.join(cif_folder, cif_file)
            extract_ids_from_polymer(cif_path, get_polymer_type())
    elif get_molecule_type():
        for cif_file in os.listdir(cif_folder):
            cif_path = os.path.join(cif_folder, cif_file)
            extract_ids_from_molecule(cif_path, get_molecule_type())
    else:
        raise TypeError("Polimero o Molecola mancante")
    print(f"Molecole estratte da tutti i file mmCIF presenti nella cartella '{cif_folder}'")
    print("--------------------------------------------------")

def move_pdb_files():
    """
    Docstring in `cif_pdb_converte()`
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdb_folder = 'files_pdb_id'
    if os.path.exists(pdb_folder):
        for file_name in os.listdir(pdb_folder):
            file_path = os.path.join(pdb_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(pdb_folder)
    for file in os.listdir(root_dir):
        if file.endswith(".pdb"):
            src_path = os.path.join(root_dir, file)
            dst_path = os.path.join(pdb_folder, file)
            shutil.move(src_path, dst_path)
    print("Convertiti tutti i files mmCIF presenti nella cartella 'files_cif_id' in PDB")
    print("--------------------------------------------------")

def delete_txt_files_from_main():
    """
    Docstring in `cif_pdb_converte()`
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if os.path.isfile(file_path) and file.endswith(".txt") and file != "requirements.txt":
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Errore durante l'eliminazione di {file}: {e}")

def cif_pdb_converter():
    """
    Converte file mmCIF in formato PDB utilizzando il tool esterno BeEM.

    Per ogni file `.cif` presente nella cartella `files_cif_id`, viene eseguito BeEM con
    il nome del file come input. Dopo la conversione:
    - i file PDB generati vengono spostati tramite `move_pdb_files()`
    - eventuali file `.txt` superflui nella directory principale
      vengono rimossi con `delete_txt_files_from_main()`
    
    Raises:
        subprocess.CalledProcessError: Se il comando BeEM fallisce per uno dei file.
    """
    beem_executable = "BeEM.exe"
    cif_folder = "files_cif_id"
    for cif_file in os.listdir(cif_folder):
        pdb_id = os.path.splitext(cif_file)[0]
        command = f'"{beem_executable}" -p={pdb_id} {cif_folder}\\{cif_file}'
        subprocess.run(command, shell=True, check=True)
    move_pdb_files()
    delete_txt_files_from_main()
