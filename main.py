def estrai_pdb_id(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        contenuto = file.read()
        id_app = contenuto.split(',')
        pdb_id = {id.strip() for id in id_app}
    return pdb_id

print(estrai_pdb_id('example_PDB_ID.txt'))