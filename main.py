from src import input_function as run

run.get_valid_path()
run.insert_family()
run.insert_sequence_distance()
run.select_tools()
run.download_pdb()
run.download_fasta()

print(run.MOLECULE_FAMILY)
print(run.SEQUENCE_DISTANCE)
print(run.SELECTED_TOOLS)
