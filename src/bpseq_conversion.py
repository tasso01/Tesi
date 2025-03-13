import os

def extract_base_pairs(file_path):
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
    if not check_total_base_pairs(extracted_lines):
        return []
    return clean_base_pairs_list(extracted_lines)

def check_total_base_pairs(base_pairs_list):
    if not base_pairs_list:
        return False
    last_line = base_pairs_list[-1]
    try:
        total_pairs = int(last_line.split('=')[-1].strip().split()[0])
        return total_pairs != 0
    except (IndexError, ValueError):
        return False

def clean_base_pairs_list(base_pairs_list):
    cleaned_list = []
    for line in base_pairs_list:
        if line.startswith("BEGIN_base-pair"):
            continue
        if line.startswith("END_base-pair"):
            break
        cleaned_list.append(line)
    return format_base_pairs(cleaned_list)

def format_base_pairs(base_pairs_list):
    formatted_list = []
    for line in base_pairs_list:
        parts = line.split()
        if len(parts) >= 4:
            num1, num2 = parts[0].split('_')
            num1, num2 = num1.strip(','), num2.strip(',')
            base1, base2 = parts[3][0], parts[3][2]
            formatted_list.append(f"{num1} {num2} {base1} {base2}")
    first = first_bpseq(formatted_list)
    second = second_bpseq(formatted_list)
    return bpseq_lines(first, second)

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

def bpseq_lines(first_half, second_half):
    return first_half + second_half

def rnaview_bpseq():
    input_folder = "rnaview"
    output_folder = "rnaview_bpseq"
    os.makedirs(output_folder, exist_ok=True)
    print(f"Cartella '{output_folder}' con i bpseq creata.")
    print("--------------------------------------------------")
    for filename in os.listdir(input_folder):
        if filename.endswith(".out"):
            file_path = os.path.join(input_folder, filename)
            base_pairs_section = extract_base_pairs(file_path)
            if base_pairs_section:
                output_file = os.path.join(output_folder, filename.replace(".pdb.out", ".bpseq"))
                with open(output_file, 'w', encoding='utf-8') as bpseq_file:
                    for line in base_pairs_section:
                        bpseq_file.write(line + '\n')
