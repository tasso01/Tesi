"""
Modulo per l'esecuzione automatica degli strumenti esterni di analisi strutturale su file PDB.

Funzionalità principali:
- Avvia il tool selezionati in input
- Gestisce l'esecuzione di ciascun tool su file presenti in `files_pdb_id`
  e salva gli output nelle relative cartelle.
"""
import os
import subprocess
import shutil
from src import get_tool

def run_tool():
    """
    Esegue il tool selezionato in base al valore impostato nella pipeline.
    """
    tool_to_run = get_tool()
    match tool_to_run:
        case "fr3d":
            fr3d()
        case "barnaba":
            barnaba()
        case "rnaview":
            rnaview()

def remove_out_files_from_root():
    """
    Docstring in `rnaview()`
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = [f for f in os.listdir(root_dir) if os.path.isfile(os.path.join(root_dir, f))]
    for file in files:
        if file.endswith(".out"):
            file_path = os.path.join(root_dir, file)
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Errore nell'eliminazione di {file}: {e}")

def remove_unused_rnaview():
    """
    Docstring in `rnaview()`
    """
    folder_path = "files_pdb_id"
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            if not (file.endswith(".pdb") or file.endswith(".pdb.out")) or file.endswith(".pdb_tmp.pdb"):
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Errore nell'eliminazione di {file}: {e}")

def move_pdb_out_files():
    """
    Docstring in `rnaview()`
    """
    source_folder = "files_pdb_id"
    destination_folder= "output\\rnaview"
    files = os.listdir(source_folder)
    for file in files:
        if file.endswith(".pdb.out"):
            src_path = os.path.join(source_folder, file)
            dest_path = os.path.join(destination_folder, file)
            try:
                shutil.move(src_path, dest_path)
            except OSError as e:
                print(f"Errore nello spostamento di {file}: {e}")

def rnaview():
    """
    Applica il tool RNAView a tutti i PDB presenti nella cartella `files_cid_id`
    Elimina i file di output non necessari e li orgnaizza con:
    - `remove_out_files_from_root()`
    - `remove_unused_rnaview()`
    - `move_pdb_out_files()`
    """
    folder_path = "files_pdb_id"
    destination_folder= "output\\rnaview"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    pdb_files = [f for f in os.listdir(folder_path)]
    for pdb_file in pdb_files:
        pdb_path = os.path.join(folder_path, pdb_file)
        subprocess.run(["rnaview", pdb_path], check=True)
    remove_unused_rnaview()
    remove_out_files_from_root()
    move_pdb_out_files()
    print("--------------------------------------------------")
    print(f"Cartella '{destination_folder}' con gli output creata.")
    print("--------------------------------------------------")

def clean_fr3d_output():
    """
    Docstring in `fr3d()`
    """
    destination_folder = "output\\fr3d"
    for filename in os.listdir(destination_folder):
        if filename.endswith("_basepair.txt"):
            new_filename = filename.replace("_basepair", "")
            old_path = os.path.join(destination_folder, filename)
            new_path = os.path.join(destination_folder, new_filename)
            os.rename(old_path, new_path)

def fr3d():
    """
    Applica il tool FR3D a tutti i PDB presenti nella cartella `files_cid_id`
    Riscrive i nomi dei file di output con `clean_fr3d_output()`.
    """
    destination_folder = "output\\fr3d"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdb_dir = os.path.join(root_dir, "files_pdb_id")
    output_dir = os.path.join(root_dir, destination_folder)
    application_dir = os.path.join(root_dir, "fr3d-python", "fr3d", "classifiers")
    pdb_files = [f for f in os.listdir(pdb_dir)]
    os.chdir(application_dir)
    for pdb_file in pdb_files:
        pdb_id = os.path.splitext(pdb_file)[0]
        comando = [
            "python", "NA_pairwise_interactions.py",
            "-i", pdb_dir,
            "-o", output_dir,
            pdb_id
        ]
        subprocess.run(comando, check=True)
    os.chdir(root_dir)
    clean_fr3d_output()
    print("--------------------------------------------------")
    print(f"Cartella '{destination_folder}' con gli output creata.")
    print("--------------------------------------------------")

def move_barnaba_out(pdb_id):
    """
    Docstring in `barnaba()`
    """
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(root_dir, "output\\barnaba")
    for filename in os.listdir(root_dir):
        file_path = os.path.join(root_dir, filename)
        if filename.endswith(".stacking.out"):
            os.remove(file_path)
        elif filename.endswith(".pairing.out"):
            new_name = f"{pdb_id}.pairing.out"
            new_path = os.path.join(target_dir, new_name)
            shutil.move(file_path, new_path)

def barnaba():
    """
    Applica il tool Barnaba a tutti i PDB presenti nella cartella `files_cid_id`
    Organizza gli output con `move_barnaba_out()`.
    """
    destination_folder = "output\\barnaba"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    pdb_folder = "files_pdb_id"
    barnaba_script = "barnaba-master/bin/barnaba"
    for filename in os.listdir(pdb_folder):
        if filename.endswith(".pdb"):
            pdb_id = os.path.splitext(filename)[0]
            file_path = os.path.join(pdb_folder, filename)
            command = ["python", barnaba_script, "ANNOTATE", "--pdb", file_path]
            subprocess.run(command, check=True)
            move_barnaba_out(pdb_id)
    print("--------------------------------------------------")
    print(f"Cartella '{destination_folder}' con gli output creata.")
    print("--------------------------------------------------")
