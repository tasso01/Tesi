from src import input_function, cif_elaboration

input_function.get_valid_path()
input_function.insert_family()
input_function.select_tools()

cif_elaboration.process_all_cif_files()
cif_elaboration.cif_pdb_converter()
