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
    extract_atoms_from_ids2(mmcif_file, entity_ids)

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
    extract_atoms_from_ids2(mmcif_file, entity_ids)

def process_all_cif_files():
    cif_directory = "files_cif"
    cif_files = [f for f in os.listdir(cif_directory) if f.endswith(".cif")]
    if not cif_files:
        print("Nessun file .cif trovato nella cartella")
        return
    destination_folder = "files_cif_id"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
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
    print(f"Molecole estratte da tutti i file mmCIF presenti nella cartella '{cif_directory}'")
    print("--------------------------------------------------")

def move_pdb_files():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdb_folder = os.path.join(root_dir, 'files_pdb_id')
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
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if os.path.isfile(file_path) and file.endswith(".txt") and file != "requirements.txt":
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Errore durante l'eliminazione di {file}: {e}")

def cif_pdb_converter():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    beem_executable_path = os.path.join(root_dir, "BeEM.exe")
    cif_folder = "files_cif_id"
    cif_files = [f for f in os.listdir(cif_folder) if f.endswith(".cif")]
    for cif_file in cif_files:
        file_name_without_ext = os.path.splitext(cif_file)[0]
        command = f'"{beem_executable_path}" -p={file_name_without_ext} {cif_folder}\\{cif_file}'
        subprocess.run(command, shell=True, check=True)
    move_pdb_files()
    delete_txt_files_from_main()

def extract_atoms_from_ids2(file_cif, entity_ids):
    cif_dict = MMCIF2Dict(file_cif)
    for key in ["_atom_site.group_PDB", "_atom_site.label_entity_id"]:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    label_entity_ids = list(map(int, cif_dict["_atom_site.label_entity_id"]))
    entity_ids = set(entity_ids)
    atom_indices = set()
    for i, (g, eid) in enumerate(zip(group_pdb, label_entity_ids)):
        if g == "ATOM" and eid in entity_ids:
            atom_indices.add(i + 1)
    if not atom_indices:
        print(f"Nessun ATOM trovato per gli entity_id forniti in '{file_cif}'")
        return
    output_directory = "files_cif_id"
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    output_file = os.path.join(output_directory, f"{pdb_id}_filtered.cif")
    with open(file_cif, encoding='utf-8') as infile:
        lines = infile.readlines()
    with open(output_file, "w", encoding='utf-8') as outfile:
        for line in lines:
            if line.startswith("_atom_site.") or (line.startswith("ATOM") and int(line.split()[1]) in atom_indices):
                outfile.write(line)
    print(f"ATOM di {pdb_id} per gli entity_id {entity_ids} salvati in {output_file}")
