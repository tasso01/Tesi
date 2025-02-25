import re
import shutil
import os
import requests
from src import MOLECULE_FAMILY, TOOLS, SELECTED_TOOLS

def get_valid_path():
    while True:
        path_check = input("Inserisci un percorso valido (cartella o file .txt): ").strip('"')
        if os.path.isdir(path_check):
            if all(f.endswith('.cif') for f in os.listdir(path_check)):
                print(f"Valid input path: {path_check}")
                copy_folder(path_check)
                return
            else:
                print("Errore: La cartella deve contenere solo file .cif")
        elif os.path.isfile(path_check) and path_check.lower().endswith(".txt"): 
            with open(path_check, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if all(part.strip().isalnum() for part in content.split(',')):
                    print(f"Valid input path: {path_check}")
                    download_cif(path_check)
                    return
                else:
                    print("Errore: Il file .txt deve contenere solo PDB_ID separati da virgole")
        else:
            print("Errore: Il percorso non è una cartella né un file .txt")

def copy_folder(source_path):
    destination_path = "files_cif"
    if os.path.exists(destination_path):
        print(f"Esiste già una cartella con il nome '{destination_path}' nella destinazione")
        return
    try:
        shutil.copytree(source_path, destination_path)
        print(f"Cartella copiata nel progetto in {destination_path}")
    except shutil.Error as e:
        print(f"Errore durante la copia della cartella: {e}")

def download_cif(source_path):
    destination_path = "files_cif"
    if os.path.exists(destination_path):
        print(f"LEsiste già una cartella con il nome '{destination_path}' nella destinazione")
        return
    os.makedirs(destination_path)
    with open(source_path, "r", encoding='utf-8') as file:
        content = file.read().strip()
    id_pdbs = content.split(",")
    base_url = "https://files.rcsb.org/download/{}.cif"
    for pdb_id in id_pdbs:
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

def insert_family():
    global MOLECULE_FAMILY
    MOLECULE_FAMILY = input("Inserisci il nome della famiglia (o premi invio per continuare): ")
    print(f"Famiglia selezionata: {MOLECULE_FAMILY}")

def select_tools():
    global SELECTED_TOOLS
    while len(SELECTED_TOOLS) < len(TOOLS):
        print("\nLista dei tool disponibili:")
        for index, tool in enumerate(TOOLS, start=1):
            print(f"{index}. {tool}")
        if SELECTED_TOOLS:
            user_input = input("\nInserisci il numero di un tool da selezionare (o 'next' per terminare): ").strip()
        else:
            user_input = input("\nInserisci il numero di un tool da selezionare: ").strip()
        if user_input.lower() == "next":
            if SELECTED_TOOLS:
                return
            else:
                print("Devi selezionare almeno un tool prima di terminare.")
                continue
        if user_input.isdigit():
            tool_index = int(user_input)
            if 1 <= tool_index <= len(TOOLS):
                selected_tool = TOOLS[tool_index - 1]
                if selected_tool in SELECTED_TOOLS:
                    print("Questo tool è già stato selezionato. Scegline un altro.")
                else:
                    SELECTED_TOOLS.add(selected_tool)
                    print(f"Aggiunto: {selected_tool}")
                    if len(SELECTED_TOOLS) == len(TOOLS):
                        print("Hai selezionato tutti i tool disponibili.")
                        return
            else:
                print("Numero fuori intervallo. Riprova.")
        else:
            print("Input non valido. Inserisci un numero tra 1 e 6.")

def download_pdb():
    cif_folder="files_cif"
    pdb_folder="files_pdb"
    if os.path.exists(pdb_folder):
        print(f"La cartella '{pdb_folder}' esiste già")
        return
    if not(os.path.exists(cif_folder)):
        print(f"La cartella '{cif_folder}' non esiste")
        return
    os.makedirs(pdb_folder)
    base_url = "https://files.rcsb.org/download/{}.pdb"
    for filename in os.listdir(cif_folder):
        if filename.endswith(".cif"):
            pdb_id = os.path.splitext(filename)[0]
            url = base_url.format(pdb_id)
            file_path = os.path.join(pdb_folder, f"{pdb_id}.pdb")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Scaricato {pdb_id}.pdb")
            except requests.RequestException as e:
                print(f"Errore nel download di {pdb_id}: {e}")

def download_fasta():
    pdb_folder="files_pdb"
    fasta_folder="files_fasta"
    if os.path.exists(fasta_folder):
        print(f"La cartella '{fasta_folder}' esiste già")
        return
    if not(os.path.exists(pdb_folder)):
        print(f"La cartella '{pdb_folder}' non esiste")
        return
    os.makedirs(fasta_folder)
    base_url = "https://www.rcsb.org/fasta/entry/"
    for filename in os.listdir(pdb_folder):
        if filename.endswith(".pdb"):
            pdb_id = os.path.splitext(filename)[0]
            url = f"{base_url}{pdb_id}"
            file_path = os.path.join(fasta_folder, f"{pdb_id}.fasta")
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(file_path, "w", encoding='utf-8') as file:
                    file.write(response.text)
                print(f"Scarciato {pdb_id}.fasta")
            except requests.exceptions.RequestException as e:
                print(f"Errore nel download di {pdb_id}: {e}")

def filter_fasta_by_chain_id(chain_ids, fasta_file, output_file):
    with open(fasta_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    selected_lines = []
    save_sequence = False   
    for line in lines:
        if line.startswith('>'):
            match = re.search(r'Chain ([A-Za-z0-9]+)', line)
            if match:
                chain_id = match.group(1)
                save_sequence = chain_id in chain_ids
            else:
                save_sequence = False       
        if save_sequence:
            selected_lines.append(line)    
    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.writelines(selected_lines)
    print(f"File filtrato salvato in: {output_file}")
