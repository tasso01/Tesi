import csv
import os
import shutil
import subprocess
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src import get_molecule_family

def extract_atoms_to_cif(file_cif, molecule_id):
    cif_dict = MMCIF2Dict(file_cif)
    required_keys = ["_atom_site.group_PDB", "_atom_site.label_entity_id"]
    for key in required_keys:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    entity_ids = cif_dict["_atom_site.label_entity_id"]
    atom_indices = [i for i, (g, eid) in enumerate(zip(group_pdb, entity_ids)) if g == "ATOM" and eid == str(molecule_id)]
    if not atom_indices:
        print(f"Nessun ATOM trovato per entity_id {molecule_id} nel file {file_cif}")
        return
    output_directory = "files_cif_id"
    os.makedirs(output_directory, exist_ok=True)
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    output_file = os.path.join(output_directory, f"{pdb_id}_{molecule_id}.cif")
    with open(output_file, mode="w", encoding='utf-8') as file:
        for line in open(file_cif, encoding='utf-8'):
            if line.startswith("_atom_site."):
                file.write(line)
            elif line.split()[0] == "ATOM" and line.split()[1] in [str(i+1) for i in atom_indices]:
                file.write(line)
    print(f"Dati completi degli ATOM per entity_id {molecule_id} salvati in {output_file}")

def extract_atoms_to_csv(file_cif, molecule_id):
    cif_dict = MMCIF2Dict(file_cif)
    required_keys = ["_atom_site.group_PDB", "_atom_site.label_entity_id"]
    for key in required_keys:
        if key not in cif_dict:
            raise KeyError(f"Il file {file_cif} non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    entity_ids = cif_dict["_atom_site.label_entity_id"]
    atom_indices = [i for i, (g, eid) in enumerate(zip(group_pdb, entity_ids)) if g == "ATOM" and eid == str(molecule_id)]
    if not atom_indices:
        print(f"Nessun ATOM trovato per entity_id {molecule_id} nel file {file_cif}")
        return
    atom_data = {key: [cif_dict[key][i] for i in atom_indices] for key in cif_dict if key.startswith("_atom_site.")}
    column_names = list(atom_data.keys())
    output_directory = "files_csv"
    os.makedirs(output_directory, exist_ok=True)
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    output_file = os.path.join(output_directory, f"{pdb_id}.csv")
    with open(output_file, mode="w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)        
        rows = zip(*[atom_data[col] for col in column_names])
        writer.writerows(rows)
    print(f"Dati completi degli ATOM per entity_id {molecule_id} salvati in {output_file}")

def extract_atoms_from_family(file_cif, molecule):
    cif_dict = MMCIF2Dict(file_cif)
    entity_ids = cif_dict.get("_entity.id", [])
    descriptions = cif_dict.get("_entity.pdbx_description", [])
    if isinstance(entity_ids, str):
        entity_ids = [entity_ids]
    if isinstance(descriptions, str):
        descriptions = [descriptions]
    def clean_string(s):
        return s.strip().replace("'", "").replace('"', "")
    entity_map = {clean_string(desc): int(entity_id) for desc, entity_id in zip(descriptions, entity_ids)}
    molecule = clean_string(molecule)
    molecule_id = entity_map.get(molecule, -1)
    extract_atoms_to_cif(file_cif, molecule_id)

def process_all_cif_files():
    cif_directory = "files_cif"
    if not os.path.exists(cif_directory):
        raise FileNotFoundError(f"La cartella {cif_directory} non esiste.")
    cif_files = [f for f in os.listdir(cif_directory) if f.endswith(".cif")]
    if not cif_files:
        print("Nessun file .cif trovato nella cartella")
        return
    for cif_file in cif_files:
        cif_path = os.path.join(cif_directory, cif_file)
        molecule_family = get_molecule_family()
        if not molecule_family:
            print(f"Nessuna famiglia di molecole trovata in {cif_file}.")
            continue
        print(f"Elaborazione file: {cif_file} con molecola '{molecule_family}'...")
        extract_atoms_from_family(cif_path, molecule_family)
    print("Elaborazione completata per tutti i file .cif.")

def move_pdb_files():
    src_directory = os.path.dirname(os.path.abspath(__file__))  # Percorso della cartella src
    project_root = os.path.abspath(os.path.join(src_directory, os.pardir))  # Percorso della cartella principale
    pdb_folder = os.path.join(project_root, 'files_pdb_id')
    if not os.path.exists(pdb_folder):
        os.makedirs(pdb_folder)
    for file in os.listdir(project_root):
        if file.endswith(".pdb"):
            src_path = os.path.join(project_root, file)
            dst_path = os.path.join(pdb_folder, file)
            shutil.move(src_path, dst_path)
            print(f"Spostato: {file} -> {pdb_folder}")

def cif_pdb_converter():
    beem_executable_path = r"C:\Users\Francesco\Desktop\tesi\BeEM.exe"  
    cif_folder = "files_cif_id" 
    cif_files = [f for f in os.listdir(cif_folder) if f.endswith(".cif")]
    for cif_file in cif_files:
        file_name_without_ext = os.path.splitext(cif_file)[0]
        command = f'"{beem_executable_path}" -p={file_name_without_ext} {cif_folder}\\{cif_file}'
        print(f"Eseguendo: {command}")
        subprocess.run(command, shell=True, check=True)
    move_pdb_files()
