# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 12:44:30 2014 @author: Poorna
"""

"""Detect and plot RNA base- amino acid interactions."""
from fr3d.cif.reader import Cif
from fr3d.definitions import RNAconnections
from fr3d.definitions import RNAbaseheavyatoms
from fr3d.definitions import Ribophos_connect
from fr3d.definitions import aa_connections
from fr3d.definitions import aa_backconnect
from fr3d.definitions import aa_fg
from fr3d.definitions import nt_backbone
from fr3d.definitions import tilt_cutoff
from fr3d.definitions import planar_atoms
import numpy as np
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D



def get_structure(filename):
    with open(filename, 'rb') as raw:
        structure = Cif(raw).structure()
        """All RNA bases are placed in the standard orientation. All Hydrogen
 atoms are inferred. Rotation matrix is calculated for each base."""
        structure.infer_hydrogens()
        return structure


"""# TODO: Modify Component.atoms_within() to do what this does, return True if there
# are atoms from the second component within some distance cutoff.
def enough_atoms_near(base_residue, aa_residue, base_atoms, c):
    Calculates atom to atom distance of part "aa_part" of neighboring amino acids
    of type "aa" from each atom of base. Only returns a pair of aa/nt if two
    or more atoms are within the cutoff distance
    min_distance = 4
    n = 0
    for base_atom in base_residue.atoms(name=base_atoms):
        for aa_atom in aa_residue.atoms(name=aa_fg[aa_residue.sequence]):
            # aa_atom = atom.coordinates()
            distance = np.subtract(base_atom.coordinates(), aa_atom.coordinates())
            distance = np.linalg.norm(distance)
            #print base_residue.unit_id(), aa_residue.unit_id(), distance
            if distance <= min_distance:
                n = n+1
                #print aa_atom.name
    if n>=c:
        #print aa_residue.unit_id()
        return True"""


def enough_HBs(base_residue, aa_residue, base_atoms):
    """Calculates atom to atom distance of part "aa_part" of neighboring amino acids
    of type "aa" from each atom of base. Only returns a pair of aa/nt if two
    or more atoms are within the cutoff distance"""
    min_distance = 4
    HB_atoms = set(['N', 'NH1','NH2','NE','NZ','ND1','NE2','O','OD1','OE1','OE2', 'OG', 'OH'])
    n = 0
    for base_atom in base_residue.atoms(name=base_atoms):
        for aa_atom in aa_residue.atoms(name=aa_fg[aa_residue.sequence]):

            distance = np.subtract(base_atom.coordinates(), aa_atom.coordinates())
            distance = np.linalg.norm(distance)
            if distance <= min_distance and aa_atom.name in HB_atoms:
                n = n+1
    if n>=2:
        return True


def find_neighbors(bases, amino_acids, aa_part, dist_cent_cutoff):
    """Finds all amino acids of type "aa" for which center of "aa_part" is within
    specified distance of center of bases of type "base" and returns superposed bases"""
    #count_total = 0
    count_pair = 0
    list_aa_coord = []
    list_base_coord = []
    aas = list(amino_acids)
    aaList_len = None
    new_aaList_len = None
    list_base_aa = []

    #target = open('E:\\Leontis\\Python scripts\\RNAprotein-count_%s.txt' % PDB, 'a')
    for base_residue in bases:
        base_seq = base_residue.sequence
        if base_part == 'base':
            base_atoms = RNAbaseheavyatoms[base_seq]
        elif base_part == 'nt_backbone':
            base_atoms = nt_backbone[base_seq]

        try:
            base_center = base_residue.centers[tuple(base_atoms)]

            if not base_center.any():
                continue
        except:
            print "Incomplete residue", base_residue.unit_id()
            continue

        aaList_len = len(list_aa_coord)
        new_aaList_len = 0
        for aa_residue in aas:
            aa_center = aa_residue.centers[aa_part]
            if not aa_center.any():
                continue

            #print base_center, aa_center, aa_residue.unit_id()
            dist_vector = np.subtract(base_center, aa_center)
            dist_scalar = np.linalg.norm(dist_vector)
            if aa_residue.sequence in set (['LYS','SER', 'THR', 'TYR']):
                c= 1
            else:
                c = 2
            #base_seq = base_residue.sequence
            if dist_scalar <= dist_cent_cutoff and \
            atom_dist_basepart(base_residue, aa_residue, base_atoms, c):
                count_pair = count_pair + 1

                rotation_matrix = base_residue.rotation_matrix

                base_coordinates = {}
                for base_atom in base_residue.atoms():
                    base_key = base_atom.name
                    base_coordinates[base_key]= translate_rotate(base_atom, base_center, rotation_matrix)

                    # base_coordinates is a list of the Atoms

                aa_coordinates = {}
                for atom in aa_residue.atoms():
                    key = atom.name
                    aa_coordinates[key]= translate_rotate(atom, base_center, rotation_matrix)
                    #print key, translate_rotate(atom, base_center, base_residue)


                interaction = type_of_interaction(base_residue, aa_residue, aa_coordinates)

                #csv reader for helix-loop classification
                #with open('E:\\Leontis\\Python scripts\\CIF\\5AJ3.csv', 'rb') as f:
                    #reader = csv.reader(f)

                    #for entry in reader:
                     #   helix_list.extend(entry)

                base_aa = None
                if interaction == "pseudopair" and enough_HBs(base_residue, aa_residue, base_atoms):
                        edge = detect_edge(base_residue, base_coordinates,aa_residue, aa_coordinates)
                        #print edge
                        base_aa = annotate(base_residue, aa_residue, interaction, edge)


                elif interaction == "stacked" or interaction == "perpendicular":
                    edge = "N/A"
                    base_aa = annotate(base_residue, aa_residue, interaction, edge)

                    """if base_residue.unit_id() in helix_list:
                        secondary_structure= "Helix"
                    else:
                        secondary_structure= "Loop"
                        """

                if base_aa is not None:
                    list_base_aa.append(base_aa)

                    for base_atom in base_residue.atoms():
                        list_base_coord.append(base_coordinates)
                    for aa_atom in aa_residue.atoms():
                        list_aa_coord.append(aa_coordinates)

        new_aaList_len = len(list_base_aa)


        new_aaList_len = len(list_aa_coord)
        #list_base_residue.append(base_residue)
    try:
        if aaList_len == new_aaList_len:

            print 'No neighbors detected with %s' % aa_residue.sequence
    except:
       print "done"
    #print "%d neighbors" % count_pair + ' detected in %s' % PDB + ' with %s' % aa


    return list_base_aa, list_aa_coord, list_base_coord
    #return list_aa_coord, list_base_coord, count, list_base_aa
def annotate(base_residue, aa_residue, interaction, edge):
    base_aa = (base_residue, aa_residue, interaction, edge)
    return base_aa

def type_of_interaction(base_residue, aa_residue, aa_coordinates):
    squared_xy_dist_list = []
    aa_z =[]

    """Defines different sets of amino acids"""
    stacked_aa = set (["TRP", "TYR", "PHE", "HIS", "ARG", "LYS", "ASN", "GLN", "LEU", "ILE", "PRO", "THR"])
    #bidentate_aa = set (["ASP", "GLU", "ASN", "GLN", "ARG", "HIS", "TRP", "TYR","PHE", "ILE", "LEU"])
    pseudopair_aa = set (["ASP", "GLU", "ASN", "GLN", "HIS", "LYS", "ARG", "SER", "TYR", "TRP", "PHE", "VAL", "LEU", "ILE", "MET"])

    for aa_atom in aa_residue.atoms(name=aa_fg[aa_residue.sequence]):
        key = aa_atom.name
        aa_x= aa_coordinates[key][0]
        aa_y= aa_coordinates[key][1]

        squared_xy_dist = (aa_x**2) + (aa_y**2)
        squared_xy_dist_list.append(squared_xy_dist)

        aa_z.append(aa_coordinates[key][2])

    mean_z = np.mean(aa_z)

    #print base_residue.unit_id(), aa_residue.unit_id(), min(squared_xy_dist_list), mean_z
    if min(squared_xy_dist_list) <= 3:
        if aa_residue.sequence in stacked_aa:
            return stacking_angle(base_residue, aa_residue, min(squared_xy_dist_list))
        else:
            return stacking_tilt(aa_residue, aa_coordinates)

    elif -1.8 <= mean_z < 1.8 and aa_residue.sequence in pseudopair_aa:
            angle= angle_between_normals(base_residue, aa_residue)
            #print "pseudopair"
            #print base_residue.unit_id(), aa_residue.unit_id(), mean_z, angle

            #if stacking_tilt(aa_residue, aa_coordinates) == "stacked":
            if 0 <= angle <= 0.75 or 2.6 <= angle <= 3.14:
                return "pseudopair"
         
            
def stacking_angle (base_residue, aa_residue, min_dist):
    vec1 = normal_calculation(base_residue)
    vec2 = normal_calculation(aa_residue)
    
    stacked_aa = set (["TRP", "TYR", "PHE", "HIS", "ARG", "LYS", "LEU", "ILE", "PRO", "ASN", "GLN"])       
    perpendicular_aa = set (["TYR", "HIS", "ARG", "LYS", "ASN", "GLN", "LEU", "ILE"])
    angle = angle_between_planes(vec1, vec2)
    print "stacked"
    print base_residue.unit_id(), aa_residue.unit_id(), min_dist, angle

    if aa_residue.sequence in stacked_aa:
        if angle <=0.67 or 2.45 <= angle <= 3.15:
            return "stacked"
        elif aa_residue.sequence in perpendicular_aa:
            if 1.2<= angle <=1.64:
                return "perpendicular"


def stacking_tilt(aa_residue, aa_coordinates):
    baa_dist_list = []

    for aa_atom in aa_residue.atoms(name=aa_fg[aa_residue.sequence]):
        key = aa_atom.name
        aa_z = aa_coordinates[key][2]
        baa_dist_list.append(aa_z)
    max_baa = max(baa_dist_list)
    min_baa = min(baa_dist_list)
    #print 'max distance: %s' % max_baa + ' min distance: %s' % min_baa
    diff = max_baa - min_baa
    #print aa_residue.unit_id(), diff
    if diff <= tilt_cutoff[aa_residue.sequence]:
        return "stacked"

# TODO: Should be equivlant to Component.transform(matrix), if the method in
# Component is not equivlant, then lets change it. Look at the tests in
# tests/data/component_tests.py for TransformTest.
def translate_rotate(atom, reference, rotation_matrix):
     atom_coord = atom.coordinates()
     dist_translate = np.subtract(atom_coord, reference)
     dist_aa_matrix = np.matrix(dist_translate)
     #rotation_matrix = base_residue.rotation_matrix
     #transposed_rotation = rotation_matrix.transpose()
     rotated_atom = dist_aa_matrix * rotation_matrix
     coord_array = np.array(rotated_atom)
     a = coord_array.flatten()
     coord = a.tolist()
     return coord

def detect_edge(base_residue, base_coordinates, aa_residue, aa_coordinates):
    aa_x = 0
    aa_y = 0
    n = 0
    base_x = 0
    base_y = 0
    for aa_atom in aa_residue.atoms(name=aa_fg[aa_residue.sequence]):
        key = aa_atom.name
        aa_x+= aa_coordinates[key][0]
        aa_y+= aa_coordinates[key][1]
        n +=1
    aa_center_x = aa_x/n
    aa_center_y = aa_y/n

    for base_atom in base_residue.atoms(name=RNAbaseheavyatoms[base_residue.sequence]):
        key = base_atom.name
        base_x+= base_coordinates[key][0]
        base_y+= base_coordinates[key][1]
        n +=1
    base_center_x = aa_x/n
    base_center_y = aa_y/n

    y = aa_center_y - base_center_y
    x = aa_center_x - base_center_x
    angle_aa = np.arctan2(y,x)
    #print base_residue.unit_id(), aa_residue.unit_id(),angle_aa
    if -1 <= angle_aa <= 0:
        return "Sugar"
    elif angle_aa <=1:
        return "WC"
    elif 1.4 <= angle_aa <= 3.2:
        return "Hoogsteen"


ChainNames = {}

ChainNames ['5AJ3'] = {'B' :'uS2m' , 'C': 'uS3m/ uS24m', 'E':'uS5m', 'F':'bS6m',
                       'G':'uS7m', 'I':'uS9m', 'J':'uS10m', 'K':'uS11m', 'L':'uS12m',
                       'N':'uS14m', 'O':'uS15m','P':'bS16m','Q':'uS17m',
                       'R':'uS18m/ uS18c', 'T':'bL19m', 'U':'bS21m','a':'mS22',
                       'b':'mS23', 'c':'mS25', 'd': 'mS26', 'e':'mS27', 'f':'bS1m/mS28',
                       'g':'mS29','h':'mS31','i':'mS33','j':'mS34','k':'mS35','m':'mS37',
                       'n':'mS38','o':'mS39','p':'mS40'}


ChainNames ['3J9M'] = {'B' :'uS2m' , 'C': 'uS3m/ uS24m', 'D':'uS5m',
                       'E':'bS6m', 'F':'uS7m', 'G':'uS9m', 'H':'uS10m',
                       'I':'uS11m', 'J':'uS12m', 'K':'uS14m', 'L':'uS15m',
                       'M':'bS16m', 'N':'uS17m', 'O':'bS18b/ mS40','P':'uS18m/ uS18c',
                       'Q':'bS21m', 'R':'mS22', 'S':'mS23', 'T':'mS25', 'U':'mS26',
                       'V': 'mS27', 'W':'bL27m','X':'mS29', 'Y':'mS31','Z':'mS33','0': 'bL32m',
                       '1': 'bL33m', '2': 'bL34m', '3': 'bL35m', '4': 'bL36m',
                       '5': 'mL37','6': 'mL38','7': 'mL39', '8': 'mL40','9': 'mL41',
                       'a':'mS34', 'b':'mS35', 'c':'mS37', 'd': 'mS38', 'e':'ms39', 'f':'mL48',
                       'g':'mL49','h':'mL50','i':'mL51','j':'mL52','k':'mL53','l':'mL54',
                       'm':'bL31m', 'o':'mL63','p':'mL62','q':'mL62', 'r':'mL66/bS18a',
                       's':'mL65/ mS30', 'AB':'uS2m','AC':'uS3m', 'AD':'uS5m',
                       'AE':'bS6m', 'AF':'uS7m','AG':'uS9m', 'AH':'uS10m','AI':'uS11m',
                       'AJ':'uS12m', 'AK':'uS14m', 'AL':'uS15m','AM':'bS16m','AN':'uS17m',
                       'AO':'mS40/ bS18b', 'AP':'bS18m/ bS18c','AQ':'bS21m','AR':'mS22',
                       'AS': 'mS23','AT': 'mS25','AU': 'mS26','AV': 'mS27','AW': 'bS21m',
                       'AX': 'mS29','AY': 'mS31','AZ': 'mS33','A0': 'mS34','A1': 'mS35',
                       'A2': 'mS37','A3': 'mS38','A4': 'mS39',}

ChainNames ['3I8G'] = {'B':'bS1', 'E' :'uS2', 'F' :'uS3', 'G' :'uS4', 'H' :'uS5', 'I' :'bS6',
                       'J' :'uS7', 'K' :'uS8', 'L' :'uS9', 'M' :'uS10', 'N' :'uS11',
                       'O' :'uS12', 'P' :'uS13', 'Q': 'uS14', 'R' :'uS15', 'S' :'bS16',
                       'T' :'bS17', 'U' :'uS18', 'V' :'uS19', 'W' :'bS20', 'X' :'bS21'}

ChainNames ['2AW7'] = {'B' :'uS2', 'C' :'uS3', 'D' :'uS4', 'E' :'uS5', 'F' :'bS6',
                       'G' :'uS7', 'H' :'uS8', 'I' :'uS9', 'J' :'uS10', 'K' :'uS11',
                       'L' :'uS12', 'M' :'uS13', 'N': 'uS14', 'O' :'uS15', 'P' :'bS16',
                       'Q' :'uS17', 'R' :'bS18', 'S' :'uS19', 'T' :'bS20', 'U' :'bS21'}

def text_output(result_list):
    with open('E:\\Leontis\\Python scripts\\Outputs\\proteinRNA_%s.txt' % PDB, 'wb') as target:
        for result in result_list:
            target.write(str(result))
            target.write("\r\n")
            target.close

def true_bidentate(result_list):
    aa_list = []
    bidentate_resi = set()
    final_result = []

    for base_residue, aa_residue, interaction in result_list:
            #base = base_residue.unit_id()
            #aa = aa_residue.unit_id()
            if interaction == "bidentate":
                if aa_residue in aa_list:
                    bidentate_resi.update({aa_residue})
                else:
                    aa_list.append(aa_residue)
            else:
                base_aa_tuple = (base_residue, aa_residue, interaction)
                final_result.append(base_aa_tuple)

    for base_residue, aa_residue, interaction in result_list:
        if aa_residue in bidentate_resi:
            base_aa_tuple = (base_residue, aa_residue, interaction)
            final_result.append(base_aa_tuple)

    return final_result

def csv_output(result_list):
    with open('E:\\Leontis\\Python scripts\\Outputs\\aa-fg_nt_%s.csv' % PDB, 'wb') as csvfile:
        fieldnames = ['RNA Chain ID', 'RNA residue','RNA residue number','Protein Chain ID', 'AA residue','AA residue number', 'Interaction', 'Edge']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for base_residue, aa_residue, interaction, edge in result_list:
            base = base_residue.unit_id()
            aa = aa_residue.unit_id()
            #print base, aa, interaction
            base_component = str(base).split("|")
            aa_component = str(aa).split("|")
            writer.writerow({'RNA Chain ID': base_component[2], 'RNA residue':base_component[3],'RNA residue number': base_component[4],'Protein Chain ID':aa_component[2],'AA residue': aa_component[3],'AA residue number': aa_component[4], 'Interaction': interaction, 'Edge': edge})

        """for base_residue, aa_residue,interaction in result_list:
                    base_component = str(base_residue).split("|")
                    aa_component = str(aa_residue).split("|")
                    writer.writerow({'RNA Chain ID': base_component[2], 'RNA residue':base_component[3],'RNA residue number': base_component[4],'Protein Chain ID':ChainNames[PDB][aa_component[2]],'AA residue': aa_component[3],'AA residue number': aa_component[4], 'Interaction': interaction})"""



def draw_base(base_seq, ax):
    """Connects atoms to draw neighboring bases and amino acids for 3D plots"""
     #creates lists of rotated base coordinates
    for basecoord_list in list_base_coord:
        new_base_x = []
        new_base_y = []
        new_base_z = []

        back_base_x = []
        back_base_y = []
        back_base_z = []


        try:
            for atomname in RNAconnections[base_seq]:
                coord_base = []
                coord_base= basecoord_list[atomname]
                new_base_x.append(coord_base[0])
                new_base_y.append(coord_base[1])
                new_base_z.append(coord_base[2])
            base_lines= ax.plot(new_base_x, new_base_y, new_base_z, label= 'Base')
            #ax.scatter(basecenter[0], basecenter[1], basecenter[2], zdir='y', color='b', marker='o')
            #ax.scatter(x = 0, y= 0, z= 0, color='b', marker='o')
            plt.setp(base_lines, 'color', 'b', 'linewidth', 1.0)

            for atomname in Ribophos_connect[base_seq]:
                back_base=[]
                back_base= basecoord_list[atomname]
                back_base_x.append(back_base[0])
                back_base_y.append(back_base[1])
                back_base_z.append(back_base[2])
            base_lines= ax.plot(back_base_x, back_base_y, back_base_z, label= 'Base')
            plt.setp(base_lines, 'color', 'g', 'linewidth', 1.0)
            #ax.text(9, 1, 1, base_residue)
        except:
            print "Missing residues"
            continue

def draw_aa(aa, ax):
    #Connects atoms to draw neighboring bases and amino acids for 3D plots
    for aacoord_list in list_aa_coord:
        new_aa_x=[]
        new_aa_y=[]
        new_aa_z=[]

        back_aa_x=[]
        back_aa_y=[]
        back_aa_z=[]

        try:
            for atomname in aa_connections[aa]:
                coord_aa=[]
                coord_aa= aacoord_list[atomname]
                new_aa_x.append(coord_aa[0])
                new_aa_y.append(coord_aa[1])
                new_aa_z.append(coord_aa[2])
            aa_lines= ax.plot(new_aa_x, new_aa_y, new_aa_z, label= 'Amino acid')
            plt.setp(aa_lines, 'color', 'r', 'linewidth', 1.0)

            for atomname in aa_backconnect[aa]:
                back_aa=[]
                back_aa= aacoord_list[atomname]
                back_aa_x.append(back_aa[0])
                back_aa_y.append(back_aa[1])
                back_aa_z.append(back_aa[2])
            aa_lines= ax.plot(back_aa_x, back_aa_y, back_aa_z, label= 'Amino acid')
            plt.setp(aa_lines, 'color', 'y', 'linewidth', 1.0)
        except:
            print "Missing residues"
            continue

def draw_aa_cent(aa, aa_part, ax):
    #Connects atoms to draw neighboring bases and amino acids for 3D plots
    for aacoord_list in list_aa_coord:
        new_aa_x=[]
        new_aa_y=[]
        new_aa_z=[]

        aa_center_x = 0
        aa_center_y = 0
        aa_center_z = 0
        n = 0

        if aa_part == 'aa_fg':
            connections = aa_connections
        elif aa_part == 'aa_backbone':
            connections = aa_backconnect
        try:
            for atomname in connections[aa]:
                coord_aa=[]
                coord_aa= aacoord_list[atomname]
                new_aa_x.append(coord_aa[0])
                new_aa_y.append(coord_aa[1])
                new_aa_z.append(coord_aa[2])

                aa_center_x = aa_center_x + coord_aa[0]
                aa_center_y = aa_center_y + coord_aa[1]
                aa_center_z = aa_center_z + coord_aa[2]
                n = n + 1
            ax.scatter(aa_center_x/n, aa_center_y/n, aa_center_z/n, c= 'r', marker = 'o')
        except:
            print "Missing residues"
            continue

"""Inputs a list of PDBs of interest to generate super-imposed plots"""
PDB_List = ['3I8G']
base_seq_list = ['A', 'U', 'C', 'G']
aa_list = ['ALA','VAL','ILE','LEU','ARG','LYS','HIS','ASP','GLU','ASN','GLN','THR','SER','TYR','TRP','PHE','PRO','CYS','MET']
#aa_list = ['PRO', 'TRP']

#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')

"""Inputs base, amino acid, aa_part of interest and cut-off distance for subsequent functions"""
if __name__=="__main__":
    for PDB in PDB_List:
        structure = get_structure('E:\\Leontis\\Python scripts\\CIF\\%s.cif' % PDB)
        result_nt_aa = []

        aa_part = 'aa_fg'
        base_part = 'base'


        bases = structure.residues(sequence= base_seq_list)
        amino_acids = structure.residues(sequence=aa_list)

        list_base_aa, list_aa_coord, list_base_coord = find_neighbors(bases, amino_acids, aa_part, 10)

        """ 3D plots of base-aa interactions
        for base, aa, interaction in list_base_aa:
            base_seq = base.sequence
            aa= aa.sequence

            draw_base(base_seq, ax)
            draw_aa(aa, ax)
            #draw_aa_cent(aa, aa_part, ax)

            ax.set_xlabel('X Axis')
            ax.set_ylabel('Y Axis')
            ax.set_zlabel('Z Axis')
            ax.set_xlim3d(10, -15)
            ax.set_ylim3d(10, -15)
            ax.set_zlim3d(10, -15)
            plt.title('%s with ' % base_seq +'%s' % aa + ' %s' % aa_part)
            plt.show()
                      """
        #making the list of resultant RNA-aa pairs
        result_nt_aa.extend(list_base_aa)

        #writing out output files
        #text_output(result_nt_aa)
<<<<<<< HEAD
            
=======

>>>>>>> origin/develop
        csv_output(result_nt_aa)
