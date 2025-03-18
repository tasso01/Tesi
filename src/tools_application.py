import os
import subprocess
import shutil
from src import bpseq_conversion, get_tool

def run_tool():
    tool_to_run = get_tool()
    match tool_to_run:
        case "RNApolis Annotator":
            pass
        case "FR3D":
            fr3d()
            bpseq_conversion.fr3d_bpseq()
        case "bpnet":
            pass
        case "baRNAba":
            pass
        case "RNAView":
            rnaview()
            bpseq_conversion.rnaview_bpseq()
        case "MC-Annotate":
            pass

def remove_out_files_from_root():
    root_folder = os.path.dirname(os.path.abspath(__file__))
    root_folder = os.path.dirname(root_folder)
    files = [f for f in os.listdir(root_folder) if os.path.isfile(os.path.join(root_folder, f))]
    for file in files:
        if file.endswith(".out"):
            file_path = os.path.join(root_folder, file)
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Errore nell'eliminazione di {file}: {e}")

def remove_unused_rnaview():
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
    source_folder = "files_pdb_id"
    destination_folder= "rnaview"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    files = os.listdir(source_folder)
    for file in files:
        if file.endswith(".pdb.out"):
            src_path = os.path.join(source_folder, file)
            dest_path = os.path.join(destination_folder, file)
            try:
                shutil.move(src_path, dest_path)
            except OSError as e:
                print(f"Errore nello spostamento di {file}: {e}")
    print("--------------------------------------------------")
    print(f"Cartella '{destination_folder}' con gli output creata.")
    print("--------------------------------------------------")

def rnaview():
    folder_path = "files_pdb_id"
    pdb_files = [f for f in os.listdir(folder_path) if f.endswith('.pdb')]
    for pdb_file in pdb_files:
        pdb_path = os.path.join(folder_path, pdb_file)
        try:
            subprocess.run(["rnaview", pdb_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Errore nell'esecuzione di rnaview per {pdb_file}: {e}")
    remove_unused_rnaview()
    remove_out_files_from_root()
    move_pdb_out_files()

def fr3d():
    destination_folder = "fr3d"
    if os.path.exists(destination_folder):
        for file_name in os.listdir(destination_folder):
            file_path = os.path.join(destination_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(destination_folder)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(root_dir)
    pdb_dir = os.path.join(root_dir, "files_pdb_id")
    output_dir = os.path.join(root_dir, destination_folder)
    application_dir = os.path.join(root_dir, "fr3d-python", "fr3d", "classifiers")
    pdb_files = [f for f in os.listdir(pdb_dir) if f.endswith(".pdb")]
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
    print("--------------------------------------------------")
    print("Cartella 'fr3d' con gli output creata.")
    print("--------------------------------------------------")
