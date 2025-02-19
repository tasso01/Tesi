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
    return selected_tools