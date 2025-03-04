import argparse
from src import input_function, cif_elaboration

def main():
    parser = argparse.ArgumentParser(description="Line Command Args")
    parser.add_argument("percorso_file_system", type=str, help="Percorso del file system")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--famiglia", type=str, help="Tipo di molecola")
    group.add_argument("-p", "--polimero", type=str, help="Tipo di polimero")
    parser.add_argument("-t", "--tool", type=str, required=True, help="Nome del tool")
    args = parser.parse_args()
    input_function.insert_path(args.percorso_file_system)
    if args.famiglia:
        input_function.insert_family(args.famiglia)
    if args.polimero:
        input_function.insert_polymer(args.polimero)
    input_function.insert_tool(args.tool)
    cif_elaboration.process_all_cif_files()
    cif_elaboration.cif_pdb_converter()

if __name__ == "__main__":
    main()
