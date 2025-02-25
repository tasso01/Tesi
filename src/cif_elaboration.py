import csv
import os
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

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
    extract_atoms_from_entity_id(file_cif, molecule_id)

def extract_atoms_from_entity_id(file_cif, molecule_id):
    cif_dict = MMCIF2Dict(file_cif)
    required_keys = ["_atom_site.group_PDB", "_atom_site.label_entity_id"]
    for key in required_keys:
        if key not in cif_dict:
            raise KeyError(f"Il file CIF non contiene la categoria {key}.")
    group_pdb = cif_dict["_atom_site.group_PDB"]
    entity_ids = cif_dict["_atom_site.label_entity_id"]
    atom_indices = [i for i, (g, eid) in enumerate(zip(group_pdb, entity_ids)) if g == "ATOM" and eid == str(molecule_id)]
    if not atom_indices:
        print(f"⚠️ Nessun ATOM trovato per entity_id {molecule_id} nel file CIF.")
        return
    atom_data = {key: [cif_dict[key][i] for i in atom_indices] for key in cif_dict if key.startswith("_atom_site.")}
    column_names = list(atom_data.keys())
    pdb_id = os.path.splitext(os.path.basename(file_cif))[0]
    output_file = f"{pdb_id}.csv"
    with open(output_file, mode="w", newline="", encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)        
        rows = zip(*[atom_data[col] for col in column_names])
        writer.writerows(rows)
    print(f"✅ Dati completi degli ATOM per entity_id {molecule_id} salvati in '{output_file}'.")
