import os
import shutil
import subprocess
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src import get_molecule_type, get_polymer_type

def extract_atoms_from_ids(file_cif, entity_ids):
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
    entity_ids = set()
    cif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = cif_dict.get("_entity.id", [])
    molecules_types = cif_dict.get("_entity.pdbx_description", [])
    for entity_id, molecule_type in zip(entity_ids_list, molecules_types):
        if molecule_type.strip() == molecule:
            entity_ids.add(int(entity_id))
    extract_atoms_from_ids(mmcif_file, entity_ids)

def extract_ids_from_polymer(mmcif_file, polymer):
    entity_ids = set()
    cif_dict = MMCIF2Dict(mmcif_file)
    entity_ids_list = cif_dict.get("_entity_poly.entity_id", [])
    polymers_types = cif_dict.get("_entity_poly.type", [])
    for entity_id, polymer_type in zip(entity_ids_list, polymers_types):
        if polymer_type.strip() == polymer:
            entity_ids.add(int(entity_id))
    extract_atoms_from_ids(mmcif_file, entity_ids)

def process_all_cif_files():
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
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for file in os.listdir(root_dir):
        file_path = os.path.join(root_dir, file)
        if os.path.isfile(file_path) and file.endswith(".txt") and file != "requirements.txt":
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Errore durante l'eliminazione di {file}: {e}")

def cif_pdb_converter():
    beem_executable = "BeEM.exe"
    cif_folder = "files_cif_id"
    for cif_file in os.listdir(cif_folder):
        pdb_id = os.path.splitext(cif_file)[0]
        command = f'"{beem_executable}" -p={pdb_id} {cif_folder}\\{cif_file}'
        subprocess.run(command, shell=True, check=True)
    move_pdb_files()
    delete_txt_files_from_main()

def extract_atoms_from_ids2(file_cif, entity_ids):
    output_folder = "files_cif_id"
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    cif_dict = MMCIF2Dict(file_cif)
    group_pdb = cif_dict["_atom_site.group_PDB"]
    label_entity_ids = list(map(int, cif_dict["_atom_site.label_entity_id"]))
    atom_indices = {entity_id: [] for entity_id in entity_ids}
    for i, (atom, entity_id) in enumerate(zip(group_pdb, label_entity_ids)):
        if atom == "ATOM" and entity_id in entity_ids:
            atom_indices[entity_id].append(i + 1)
    with open(file_cif, encoding='utf-8') as mmCIF:
        lines = mmCIF.readlines()
    for entity_id, indices in atom_indices.items():
        output_file = os.path.join(output_folder, f"{pdb_id}_{entity_id}.cif")
        with open(output_file, "w", encoding='utf-8') as outfile:
            for line in lines:
                if line.startswith("_atom_site.") or (line.startswith("ATOM") and int(line.split()[1]) in indices):
                    outfile.write(line)
        print(f"ATOM di {pdb_id} per entity_id {entity_id} salvati in {output_file}")
