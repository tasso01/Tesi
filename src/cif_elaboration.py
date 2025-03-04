import os
import shutil
import subprocess
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src import get_molecule_type, get_polymer_type

def extract_atoms_from_ids(file_cif, entity_ids):
    cif_dict = MMCIF2Dict(file_cif)
    for key in ["_atom_site.group_PDB", "_atom_site.label_entity_id"]:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    label_entity_ids = list(map(int, cif_dict["_atom_site.label_entity_id"]))
    entity_ids = set(entity_ids)
    atom_indices = {eid: [] for eid in entity_ids}
    for i, (g, eid) in enumerate(zip(group_pdb, label_entity_ids)):
        if g == "ATOM" and eid in entity_ids:
            atom_indices[eid].append(i + 1)
    output_directory = "files_cif_id"
    os.makedirs(output_directory, exist_ok=True)
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    with open(file_cif, encoding='utf-8') as infile:
        lines = infile.readlines()
    for entity_id, indices in atom_indices.items():
        if not indices:
            print(f"Nessun ATOM trovato per entity_id '{entity_id}' in '{file_cif}'")
            continue
        output_file = os.path.join(output_directory, f"{pdb_id}_{entity_id}.cif")
        with open(output_file, "w", encoding='utf-8') as outfile:
            for line in lines:
                if line.startswith("_atom_site.") or (line.startswith("ATOM") and int(line.split()[1]) in indices):
                    outfile.write(line)
        print(f"ATOM di {pdb_id} per entity_id {entity_id} salvati in {output_file}")

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
    print(f"Molecole estratte da tutti i file mmCIF presenti nella cartella {cif_directory}")
    print("--------------------------------------------------")

def move_pdb_files():
    src_directory = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(src_directory, os.pardir))
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
