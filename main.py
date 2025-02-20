import shutil
import os
import requests

TOOLS = (
    "RNApolis Annotator",
    "FR3D",
    "bpnet",
    "baRNAba",
    "RNAView",
    "MC-Annotate"
)

def download_cif(source_path):
    destination_folder = "files_cif"
    if os.path.exists(destination_folder):
        print(f"La cartella '{destination_folder}' esiste già.")
        return
    os.makedirs(destination_folder, exist_ok=True)
    with open(source_path, "r", encoding='utf-8') as file:
        content = file.read().strip()
    id_pdbs = content.split(",")
    url_base = "https://files.rcsb.org/download/{}.cif"
    for pdb_id in id_pdbs:
        pdb_id = pdb_id.strip()
        url = url_base.format(pdb_id)
        file_path = os.path.join(destination_folder, f"{pdb_id}.cif")  
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Scaricato: {pdb_id}.cif")
        except requests.exceptions.RequestException as e:
            print(f"Errore nel download di {pdb_id}: {e}")

def copy_folder(source_path):
    destination = r"C:\Users\Francesco\Desktop\tesi"    
    destination_path = os.path.join(destination, "files_cif")
    if os.path.exists(destination_path):
        print("Esiste già una cartella con il nome 'files_cif' nella destinazione")
        return
    try:
        shutil.copytree(source_path, destination_path)
        print(f"Cartella spostata con successo in {destination_path}")
    except Exception as e:
        print(f"Errore durante lo spostamento: {e}")

def get_valid_path():
    while True:
        path_check = input("Inserisci un percorso valido (cartella o file .txt): ").strip('"')
        if os.path.isdir(path_check):
            if all(f.endswith('.cif') for f in os.listdir(path_check)):
                print("Percorso valido accettato_ " + path_check)
                copy_folder(path_check)
                return path_check
            else:
                print("Errore: La cartella deve contenere solo file .cif")
        elif os.path.isfile(path_check) and path_check.lower().endswith(".txt"): 
            with open(path_check, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if all(part.strip().isalnum() for part in content.split(',')):
                    print("Percorso valido accettato: " + path_check)
                    download_cif(path_check)
                    return path_check
                else:
                    print("Errore: Il file .txt deve contenere solo codici alfanumerici separati da virgole")
        else:
            print("Errore: Il percorso non è una cartella né un file .txt")
        print("---------------------------")

def select_tools():
    selected_tools = set()
    while len(selected_tools) < len(TOOLS):
        print("\nLista dei tool disponibili:")
        for index, tool in enumerate(TOOLS, start=1):
            print(f"{index}. {tool}")
        if selected_tools:
            user_input = input("\nInserisci il numero di un tool da selezionare (o 'next' per terminare): ").strip()
        else:
            user_input = input("\nInserisci il numero di un tool da selezionare: ").strip()
        if user_input.lower() == "next":
            if selected_tools:
                break
            else:
                print("Devi selezionare almeno un tool prima di terminare.")
                continue
        if user_input.isdigit():
            tool_index = int(user_input)
            if 1 <= tool_index <= len(TOOLS):
                selected_tool = TOOLS[tool_index - 1]
                if selected_tool in selected_tools:
                    print("Questo tool è già stato selezionato. Scegline un altro.")
                else:
                    selected_tools.add(selected_tool)
                    print(f"Aggiunto: {selected_tool}")        
                    if len(selected_tools) == len(TOOLS):
                        print("Hai selezionato tutti i tool disponibili.")
                        break
            else:
                print("Numero fuori intervallo. Riprova.")
        else:
            print("Input non valido. Inserisci un numero tra 1 e 6.")
    print(selected_tools)
    return selected_tools

def download_pdb():
    cif_folder="files_cif"
    pdb_folder="files_pdb"
    if os.path.exists(pdb_folder):
        print(f"La cartella '{pdb_folder}' esiste già.")
        return
    if not(os.path.exists(cif_folder)):
        print(f"La cartella '{cif_folder}' non esiste.")
        return
    os.makedirs(pdb_folder, exist_ok=True)
    for filename in os.listdir(cif_folder):
        if filename.endswith(".cif"):
            pdb_id = filename.split(".")[0]
            pdb_url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
            output_path = os.path.join(pdb_folder, f"{pdb_id}.pdb")
            try:
                response = requests.get(pdb_url, timeout=10)
                response.raise_for_status()
                with open(output_path, "wb") as file:
                    file.write(response.content)
                print(f"Scaricato: {output_path}")
            except requests.RequestException as e:
                print(f"Errore nel download di {pdb_id}: {e}")

def download_fasta():
    pdb_folder="files_pdb"
    fasta_folder="files_fasta"
    if os.path.exists(fasta_folder):
        print(f"La cartella '{fasta_folder}' esiste già.")
        return
    if not(os.path.exists(pdb_folder)):
        print(f"La cartella '{pdb_folder}' non esiste.")
        return
    os.makedirs(fasta_folder, exist_ok=True)
    url_base_fasta = "https://www.rcsb.org/fasta/entry/"
    for file in os.listdir(pdb_folder):
        if file.endswith(".pdb"):
            pdb_id = os.path.splitext(file)[0]
            url_fasta = f"{url_base_fasta}{pdb_id}"
            try:
                response = requests.get(url_fasta, timeout=10)
                response.raise_for_status()
                fasta_path = os.path.join(fasta_folder, f"{pdb_id}.fasta")
                with open(fasta_path, "w", encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Scaricato: {pdb_id}.fasta")
            except requests.exceptions.RequestException as e:
                print(f"Errore nel download di {pdb_id}: {e}")

#try_run

#get_valid_path()
#select_tools()

#dev
