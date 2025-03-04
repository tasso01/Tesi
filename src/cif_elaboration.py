import csv
import os
import shutil
import subprocess
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src import get_molecule_type, get_polymer_type

def extract_atoms_from_ids(file_cif, molecule_ids):
    cif_dict = MMCIF2Dict(file_cif)
    required_keys = ["_atom_site.group_PDB", "_atom_site.label_entity_id"]  
    for key in required_keys:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    entity_ids = cif_dict["_atom_site.label_entity_id"] 
    atom_indices = {molecule_id: [] for molecule_id in molecule_ids}
    for i, (g, eid) in enumerate(zip(group_pdb, entity_ids)):
        if g == "ATOM" and int(eid) in molecule_ids:
            atom_indices[int(eid)].append(i)
    output_directory = "files_cif_id"
    os.makedirs(output_directory, exist_ok=True)
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    for molecule_id, indices in atom_indices.items():
        if not indices:
            print(f"Nessun ATOM trovato per entity_id '{molecule_id}' nel file '{file_cif}'")
            continue
        output_file = os.path.join(output_directory, f"{pdb_id}_{molecule_id}.cif")
        with open(output_file, mode="w", encoding='utf-8') as file:
            for line in open(file_cif, encoding='utf-8'):
                if line.startswith("_atom_site."):
                    file.write(line)
                elif line.split()[0] == "ATOM" and line.split()[1] in [str(i+1) for i in indices]:
                    file.write(line)
        print(f"Dati completi degli ATOM per entity_id {molecule_id} salvati in {output_file}")

def extract_ids_from_molecule(mmcif_file, molecule):
    entity_ids = set()
    mmcif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = mmcif_dict.get("_entity.id", [])
    entity_types = mmcif_dict.get("_entity.pdbx_description", [])
    for entity_id, entity_type in zip(entity_ids_list, entity_types):
        if entity_type.strip() == molecule:
            try:
                entity_ids.add(int(entity_id))
            except ValueError:
                continue
    extract_atoms_from_ids(mmcif_file, entity_ids)

def extract_ids_from_polymer(mmcif_file, polymer):
    entity_ids = set()
    mmcif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = mmcif_dict.get("_entity_poly.entity_id", [])
    entity_types = mmcif_dict.get("_entity_poly.type", [])
    for entity_id, entity_type in zip(entity_ids_list, entity_types):
        if entity_type.strip() == polymer:
            try:
                entity_ids.add(int(entity_id))
            except ValueError:
                continue
    extract_atoms_from_ids(mmcif_file, entity_ids)

def process_all_cif_files():
    cif_directory = "files_cif"
    if not os.path.exists(cif_directory):
        raise FileNotFoundError(f"La cartella {cif_directory} non esiste.")
    cif_files = [f for f in os.listdir(cif_directory) if f.endswith(".cif")]
    if not cif_files:
        print("Nessun file .cif trovato nella cartella")
        return
    molecule_type = get_molecule_type()
    polymer_type = get_polymer_type()
    if polymer_type:
        for cif_file in cif_files:
            cif_path = os.path.join(cif_directory, cif_file)
            extract_ids_from_polymer(cif_path, polymer_type)
    elif molecule_type:
        for cif_file in cif_files:
            cif_path = os.path.join(cif_directory, cif_file)
            extract_ids_from_molecule(cif_path, molecule_type)
    else:
        raise TypeError("Polimero o Molecola mancante")
    print(f"Molecole estratte da tutti i file mmCIF nella cartella {cif_directory}")
    print("--------------------------------------------------")

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
    print("Convertiti tutti i files mmCIF presenti nella cartella 'files_pdb_id' in PDB")
    print("--------------------------------------------------")

def cif_pdb_converter():
    beem_executable_path = r"C:\Users\Francesco\Desktop\tesi\BeEM.exe"
    cif_folder = "files_cif_id"
    if not os.path.exists(cif_folder):
        raise FileNotFoundError(f"La cartella {cif_folder} non esiste.")
    cif_files = [f for f in os.listdir(cif_folder) if f.endswith(".cif")]
    for cif_file in cif_files:
        file_name_without_ext = os.path.splitext(cif_file)[0]
        command = f'"{beem_executable_path}" -p={file_name_without_ext} {cif_folder}\\{cif_file}'
        print(f"Conversione {cif_file} to PDB")
        subprocess.run(command, shell=True, check=True)
    move_pdb_files()

#OBS

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

def extract_all_atoms_to_cif(input_cif):
    with open(input_cif, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    atom_site_section = False
    headers = []
    atom_lines = []
    for line in lines:
        if line.strip().startswith('loop_'):
            atom_site_section = True
            headers = []
            continue
        if atom_site_section:
            if line.strip().startswith('_atom_site.'):
                headers.append(line.strip())
            else:
                if headers and line.strip():
                    columns = line.split()
                    if 'ATOM' in columns:
                        atom_lines.append(line.strip())
                else:
                    atom_site_section = False
    output_directory = "files_cif_id"
    os.makedirs(output_directory, exist_ok=True)
    pdb_id = os.path.splitext(os.path.basename(input_cif))[0]
    output_file = os.path.join(output_directory, f"{pdb_id}_0.cif")
    with open(output_file, 'w', encoding='utf-8') as f:
        for header in headers:
            f.write(f"{header}\n")
        for atom in atom_lines:
            f.write(f"{atom}\n")
    print(f"File {output_file} creato con successo.")

def extract_id_from_molecule(file_cif, molecule):
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
    extract_atoms_from_id(file_cif, molecule_id)

def extract_atoms_from_id(file_cif, molecule_id):
    cif_dict = MMCIF2Dict(file_cif)
    required_keys = ["_atom_site.group_PDB", "_atom_site.label_entity_id"]
    for key in required_keys:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    entity_ids = cif_dict["_atom_site.label_entity_id"]
    atom_indices = [i for i, (g, eid) in enumerate(zip(group_pdb, entity_ids)) if g == "ATOM" and eid == str(molecule_id)]
    if not atom_indices:
        print(f"Nessun ATOM trovato per entity_id '{molecule_id}' nel file '{file_cif}'")
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
