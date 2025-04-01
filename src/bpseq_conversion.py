import os
from src import get_tool

def convert_output():
    tool_to_run = get_tool()
    match tool_to_run:
        case "fr3d":
            fr3d_bpseq()
        case "barnaba":
            barnaba_bpseq()
        case "rnaview":
            rnaview_bpseq()

def canonical_base(a, b):
    return (a == 'C' and b == 'G') or \
           (a == 'G' and b == 'C') or \
           (a == 'A' and b == 'U') or \
           (a == 'U' and b == 'A') or \
           (a == 'DC' and b == 'DG') or \
           (a == 'DG' and b == 'DC') or \
           (a == 'DA' and b == 'DT') or \
           (a == 'DT' and b == 'DA')

def first_base_pairs(base_pairs_list):
    first_half = []
    for line in base_pairs_list:
        parts = line.split()
        num1, base, num2 = parts[0], parts[2], parts[1]
        first_half.append(f"{num1} {base} {num2}")
    return first_half

def second_base_pairs(base_pairs_list):
    second_half = []
    for line in base_pairs_list[::-1]:
        parts = line.split()
        num1, base, num2 = parts[1], parts[3], parts[0]
        second_half.append(f"{num1} {base} {num2}")
    return second_half

def base_pairs_lines(first_half, second_half):
    return first_half + second_half

def base_pairs_rnaview(file_path):
    extracted_lines = []
    inside_section = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'BEGIN_base-pair' in line:
                inside_section = True
                continue
            if 'END_base-pair' in line:
                break
            if inside_section:
                extracted_lines.append(line.strip())
    return base_pairs_lines_rnaview(extracted_lines)

def base_pairs_lines_rnaview(base_pairs_list):
    canonical = []
    non_canonical = []
    for line in base_pairs_list:
        parts = line.split()
        num1, num2 = parts[0].split('_')
        num1, num2 = num1.strip(','), num2.strip(',')
        base1, base2 = parts[3][0], parts[3][2]
        if canonical_base(base1, base2):
            canonical.append(f"{num1} {num2} {base1} {base2}")
        else:
            non_canonical.append(f"{num1} {num2} {base1} {base2}")
    first_canonical = first_base_pairs(canonical)
    second_canonical = second_base_pairs(canonical)
    first_non_canonical = first_base_pairs(non_canonical)
    second_non_canonical = second_base_pairs(non_canonical)
    canonical_lines = base_pairs_lines(first_canonical, second_canonical)
    non_canonical_lines = base_pairs_lines(first_non_canonical, second_non_canonical)
    return canonical_lines, non_canonical_lines

def rnaview_bpseq():
    output_folder = "output\\rnaview"
    bpseq_folder = "output\\rnaview_bpseq"
    txt_folder = "output\\rnaview_txt"
    if os.path.exists(bpseq_folder):
        for file_name in os.listdir(bpseq_folder):
            file_path = os.path.join(bpseq_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(bpseq_folder)
    if os.path.exists(txt_folder):
        for file_name in os.listdir(txt_folder):
            file_path = os.path.join(txt_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(txt_folder)
    for filename in os.listdir(output_folder):
        if filename.endswith(".out"):
            file_path = os.path.join(output_folder, filename)
            canonical, non_canonical = base_pairs_rnaview(file_path)
            if canonical:
                output_file = os.path.join(bpseq_folder, filename.replace(".pdb.out", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in canonical:
                        bpseq_file.write(line + '\n')
            if non_canonical:
                out_file = os.path.join(txt_folder, filename.replace(".pdb.out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical:
                        txt_file.write(line + '\n')
    print(f"Cartella '{bpseq_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    print(f"Cartella '{txt_folder}' con i txt creata.")
    print("--------------------------------------------------")

def base_pairs_fr3d(file_path):
    canonical = []
    non_canonical = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split('|')
            base1, base2 = parts[3], parts[7]
            num1 = parts[4].split()[0]
            num2 = parts[8].split()[0]
            if canonical_base(base1, base2):
                canonical.append(f"{base1} {num1} {base2} {num2}")
            else:
                non_canonical.append(f"{base1} {num1} {base2} {num2}")
    return base_pairs_lines_fr3d(canonical, non_canonical)

def base_pairs_lines_fr3d(canonical, non_canonical):
    canonical_lines = []
    non_canonical_lines = []
    for line in canonical:
        parts = line.split()
        num1, base, num2 = parts[1], parts[0], parts[3]
        canonical_lines.append(f"{num1} {base} {num2}")
    for line in non_canonical:
        parts = line.split()
        num1, base, num2 = parts[1], parts[0], parts[3]
        non_canonical_lines.append(f"{num1} {base} {num2}")
    return canonical_lines, non_canonical_lines

def fr3d_bpseq():
    output_folder = "output\\fr3d"
    bpseq_folder = "output\\fr3d_bpseq"
    txt_folder = "output\\fr3d_txt"
    if os.path.exists(bpseq_folder):
        for file_name in os.listdir(bpseq_folder):
            file_path = os.path.join(bpseq_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(bpseq_folder)
    if os.path.exists(txt_folder):
        for file_name in os.listdir(txt_folder):
            file_path = os.path.join(txt_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(txt_folder)
    for filename in os.listdir(output_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(output_folder, filename)
            canonical, non_canonical = base_pairs_fr3d(file_path)
            if canonical:
                output_file = os.path.join(bpseq_folder, filename.replace(".txt", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in canonical:
                        bpseq_file.write(line + '\n')
            if non_canonical:
                out_file = os.path.join(txt_folder, filename.replace(".out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical:
                        txt_file.write(line + '\n')
    print(f"Cartella '{bpseq_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    print(f"Cartella '{txt_folder}' con i txt creata.")
    print("--------------------------------------------------")

def base_pairs_barnaba(file_path):
    extracted_lines = []
    inside_section = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("# sequence"):
                inside_section = True
                continue
            if inside_section:
                extracted_lines.append(line.strip())
    return base_pairs_lines_barnaba(extracted_lines)

def base_pairs_lines_barnaba(base_pairs_list):
    canonical = []
    non_canonical = []
    for line in base_pairs_list:
        parts = line.split()
        num1, num2 = parts[0].split("_")[1], parts[1].split("_")[1]
        base1, base2 = parts[0].split("_")[0], parts[1].split("_")[0]
        if canonical_base(base1, base2):
            canonical.append(f"{num1} {num2} {base1} {base2}")
        else:
            non_canonical.append(f"{num1} {num2} {base1} {base2}")
    first_canonical = first_base_pairs(canonical)
    second_canonical = second_base_pairs(canonical)
    first_non_canonical = first_base_pairs(non_canonical)
    second_non_canonical = second_base_pairs(non_canonical)
    canonical_lines = base_pairs_lines(first_canonical, second_canonical)
    non_canonical_lines = base_pairs_lines(first_non_canonical, second_non_canonical)
    return canonical_lines, non_canonical_lines

def barnaba_bpseq():
    output_folder = "output\\barnaba"
    bpseq_folder = "output\\barnaba_bpseq"
    txt_folder = "output\\barnaba_txt"
    if os.path.exists(bpseq_folder):
        for file_name in os.listdir(bpseq_folder):
            file_path = os.path.join(bpseq_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(bpseq_folder)
    if os.path.exists(txt_folder):
        for file_name in os.listdir(txt_folder):
            file_path = os.path.join(txt_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(txt_folder)
    for filename in os.listdir(output_folder):
        if filename.endswith(".out"):
            file_path = os.path.join(output_folder, filename)
            canonical, non_canonical = base_pairs_barnaba(file_path)
            if canonical:
                output_file = os.path.join(bpseq_folder, filename.replace(".pairing.out", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in canonical:
                        bpseq_file.write(line + '\n')
            if non_canonical:
                out_file = os.path.join(txt_folder, filename.replace(".pairing.out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical:
                        txt_file.write(line + '\n')
    print(f"Cartella '{bpseq_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    print(f"Cartella '{txt_folder}' con i txt creata.")
    print("--------------------------------------------------")
