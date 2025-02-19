import os
import requests

def from_file_to_set(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        contenuto = file.read()
        pdb_ids_app = contenuto.split(',')
        pdb_ids = {id.strip() for id in pdb_ids_app}
    return pdb_ids

def download_cif_from_set(pdb_ids, destination_folder="cif_files"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    base_url = "https://files.rcsb.org/download/"
    for pdb_id in pdb_ids:
        url = f"{base_url}{pdb_id}.cif"
        file_path = os.path.join(destination_folder, f"{pdb_id}.cif")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"Scaricato: {pdb_id}.cif")
        except requests.exceptions.RequestException as e:
            print(f"Errore nel download di {pdb_id}: {e}")

prova = from_file_to_set('example_PDB_ID.txt')
download_cif_from_set(prova)