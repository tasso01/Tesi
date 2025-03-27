import argparse
from src import input_function, cif_elaboration, tools_application, bpseq_conversion, outuput_csv

def main():
    parser = argparse.ArgumentParser(description="Line Command Args")
    parser.add_argument("file_system_path", type=str, help="Percorso del file system")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--molecola", type=str, help="Tipo di molecola")
    group.add_argument("-p", "--polimero", type=str, help="Tipo di polimero")
    parser.add_argument("-t", "--tool", type=str, required=True, help="Nome del tool")
    args = parser.parse_args()

    input_function.insert_path(args.file_system_path)
    if args.molecola:
        input_function.insert_family(args.molecola)
    if args.polimero:
        input_function.insert_polymer(args.polimero)
    input_function.insert_tool(args.tool)
    cif_elaboration.process_all_cif_files()
    cif_elaboration.cif_pdb_converter()
    tools_application.run_tool()
    bpseq_conversion.convert_output()
    outuput_csv.check_tool()

if __name__ == "__main__":
    main()
