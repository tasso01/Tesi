import os
from src import get_tool

def convert_output():
    tool_to_run = get_tool()
    match tool_to_run:
        case "FR3D":
            fr3d_bpseq()
        case "baRNAba":
            barnaba_bpseq()
        case "RNAView":
            rnaview_bpseq()

def base_pairs_rnaview(file_path):
    extracted_lines = []
    inside_section = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'BEGIN_base-pair' in line:
                inside_section = True
            if inside_section:
                extracted_lines.append(line.strip())
            if 'The total base pairs =' in line:
                break
    if not check_base_pairs_rnaview(extracted_lines):
        return []
    return clean_base_pairs_rnaview(extracted_lines)

def non_canonical_rnaview(file_path):
    extracted_lines = []
    inside_section = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if 'BEGIN_base-pair' in line:
                inside_section = True
            if inside_section:
                extracted_lines.append(line.strip())
            if 'The total base pairs =' in line:
                break
    if not check_base_pairs_rnaview(extracted_lines):
        return []
    return clean_non_canonical_rnaview(extracted_lines)

def check_base_pairs_rnaview(base_pairs_list):
    if not base_pairs_list:
        return False
    last_line = base_pairs_list[-1]
    try:
        total_pairs = int(last_line.split('=')[-1].strip().split()[0])
        return total_pairs != 0
    except (IndexError, ValueError):
        return False

def clean_base_pairs_rnaview(base_pairs_list):
    cleaned_list = []
    for line in base_pairs_list:
        if line.startswith("BEGIN_base-pair"):
            continue
        if line.startswith("END_base-pair"):
            break
        cleaned_list.append(line)
    return bpseq_lines_rnaview(cleaned_list)

def clean_non_canonical_rnaview(base_pairs_list):
    cleaned_list = []
    for line in base_pairs_list:
        if line.startswith("BEGIN_base-pair"):
            continue
        if line.startswith("END_base-pair"):
            break
        cleaned_list.append(line)
    return txt_lines_rnaview(cleaned_list)

def bpseq_lines_rnaview(base_pairs_list):
    formatted_list = []
    for line in base_pairs_list:
        parts = line.split()
        if len(parts) >= 4:
            num1, num2 = parts[0].split('_')
            num1, num2 = num1.strip(','), num2.strip(',')
            base1, base2 = parts[3][0], parts[3][2]
            if canonical_base(base1, base2):
                formatted_list.append(f"{num1} {num2} {base1} {base2}")
    first = first_bpseq(formatted_list)
    second = second_bpseq(formatted_list)
    return bpseq_lines_first_second(first, second)

def txt_lines_rnaview(base_pairs_list):
    non_canonical = []
    for line in base_pairs_list:
        parts = line.split()
        if len(parts) >= 4:
            num1, num2 = parts[0].split('_')
            num1, num2 = num1.strip(','), num2.strip(',')
            base1, base2 = parts[3][0], parts[3][2]
            if not canonical_base(base1, base2):
                non_canonical.append(f"{num1} {num2} {base1} {base2}")
    first = first_bpseq(non_canonical)
    second = second_bpseq(non_canonical)
    return bpseq_lines_first_second(first, second)

def first_bpseq(base_pairs_list):
    first_half = []
    for line in base_pairs_list:
        parts = line.split()
        num1, base, num2 = parts[0], parts[2], parts[1]
        first_half.append(f"{num1} {base} {num2}")
    return first_half

def second_bpseq(base_pairs_list):
    second_half = []
    for line in base_pairs_list[::-1]:
        parts = line.split()
        num1, base, num2 = parts[1], parts[3], parts[0]
        second_half.append(f"{num1} {base} {num2}")
    return second_half

def bpseq_lines_first_second(first_half, second_half):
    return first_half + second_half

def rnaview_bpseq():
    input_folder = "output\\rnaview"
    output_folder = "output\\rnaview_bpseq"
    out_folder = "output\\rnaview_txt"
    if os.path.exists(output_folder):
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(output_folder)
    if os.path.exists(out_folder):
        for file_name in os.listdir(out_folder):
            file_path = os.path.join(out_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(out_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".out"):
            file_path = os.path.join(input_folder, filename)
            base_pairs_section = base_pairs_rnaview(file_path)
            non_canonical_section = non_canonical_rnaview(file_path)
            if base_pairs_section:
                output_file = os.path.join(output_folder, filename.replace(".pdb.out", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in base_pairs_section:
                        bpseq_file.write(line + '\n')
            if non_canonical_section:
                out_file = os.path.join(out_folder, filename.replace(".pdb.out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical_section:
                        txt_file.write(line + '\n')
    print(f"Cartella '{output_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    print(f"Cartella '{out_folder}' con i txt creata.")
    print("--------------------------------------------------")

def base_pairs_fr3d(file_path):
    formatted_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split('|')
            base1, base2 = parts[3], parts[7]
            num1 = parts[4].split()[0]
            num2 = parts[8].split()[0]
            if canonical_base(base1, base2):
                formatted_list.append(f"{base1} {num1} {base2} {num2}")
    return bpseq_lines_fr3d(formatted_list)

def non_canonical_fr3d(file_path):
    non_canonical = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split('|')
            base1, base2 = parts[3], parts[7]
            num1 = parts[4].split()[0]
            num2 = parts[8].split()[0]
            if not canonical_base(base1, base2):
                non_canonical.append(f"{base1} {num1} {base2} {num2}")
    return bpseq_lines_fr3d(non_canonical)

def bpseq_lines_fr3d(base_pairs_list):
    bpseq_lines = []
    for line in base_pairs_list:
        parts = line.split()
        num1, base, num2 = parts[1], parts[0], parts[3]
        bpseq_lines.append(f"{num1} {base} {num2}")
    return bpseq_lines

def fr3d_bpseq():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_folder = os.path.join(root_dir, "output\\fr3d")
    output_folder = os.path.join(root_dir, "output\\fr3d_bpseq")
    out_folder = os.path.join(root_dir, "output\\fr3d_txt")
    if os.path.exists(output_folder):
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(output_folder)
    if os.path.exists(out_folder):
        for file_name in os.listdir(out_folder):
            file_path = os.path.join(out_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(out_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_folder, filename)
            base_pairs_section = base_pairs_fr3d(file_path)
            non_canonical_section = non_canonical_fr3d(file_path)
            if base_pairs_section:
                output_file = os.path.join(output_folder, filename.replace(".txt", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in base_pairs_section:
                        bpseq_file.write(line + '\n')
            if non_canonical_section:
                out_file = os.path.join(out_folder, filename.replace(".out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical_section:
                        txt_file.write(line + '\n')
    print("Cartella 'fr3d_bpseq' con i bpseq creata.")
    print("--------------------------------------------------")
    print("Cartella 'fr3d_txt' con i txt creata.")
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
    return bpseq_lines_barnaba(extracted_lines)

def non_canonical_barnaba(file_path):
    extracted_lines = []
    inside_section = False
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("# sequence"):
                inside_section = True
                continue
            if inside_section:
                extracted_lines.append(line.strip())
    return txt_lines_barnaba(extracted_lines)

def bpseq_lines_barnaba(base_pairs_list):
    formatted_list = []
    for line in base_pairs_list:
        parts = line.split()
        num1, num2 = parts[0].split("_")[1], parts[1].split("_")[1]
        base1, base2 = parts[0].split("_")[0], parts[1].split("_")[0]
        if canonical_base(base1, base2):
            formatted_list.append(f"{num1} {num2} {base1} {base2}")
    first = first_bpseq(formatted_list)
    second = second_bpseq(formatted_list)
    return bpseq_lines_first_second(first, second)

def txt_lines_barnaba(base_pairs_list):
    non_canonical = []
    for line in base_pairs_list:
        parts = line.split()
        num1, num2 = parts[0].split("_")[1], parts[1].split("_")[1]
        base1, base2 = parts[0].split("_")[0], parts[1].split("_")[0]
        if not canonical_base(base1, base2):
            non_canonical.append(f"{num1} {num2} {base1} {base2}")
    first = first_bpseq(non_canonical)
    second = second_bpseq(non_canonical)
    return bpseq_lines_first_second(first, second)

def barnaba_bpseq():
    input_folder = "output\\barnaba"
    output_folder = "output\\barnaba_bpseq"
    out_folder = "output\\barnaba_txt"
    if os.path.exists(output_folder):
        for file_name in os.listdir(output_folder):
            file_path = os.path.join(output_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(output_folder)
    if os.path.exists(out_folder):
        for file_name in os.listdir(out_folder):
            file_path = os.path.join(out_folder, file_name)
            os.remove(file_path)
    else:
        os.makedirs(out_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".out"):
            file_path = os.path.join(input_folder, filename)
            base_pairs_section = base_pairs_barnaba(file_path)
            non_canonical_section = non_canonical_barnaba(file_path)
            if base_pairs_section:
                output_file = os.path.join(output_folder, filename.replace(".out", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in base_pairs_section:
                        bpseq_file.write(line + '\n')
            if non_canonical_section:
                out_file = os.path.join(out_folder, filename.replace(".out", ".txt"))
                with open(out_file, 'w', encoding='utf-8') as txt_file:
                    for line in non_canonical_section:
                        txt_file.write(line + '\n')
    print(f"Cartella '{output_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    print(f"Cartella '{out_folder}' con i txt creata.")
    print("--------------------------------------------------")

def canonical_base(a, b):
    return (a == 'C' and b == 'G') or \
           (a == 'G' and b == 'C') or \
           (a == 'A' and b == 'U') or \
           (a == 'U' and b == 'A')
