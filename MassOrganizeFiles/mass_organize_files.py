import sys
import os
from os.path import expanduser

def read_input(filepath):
    '''
    Given
        filepath, the location of the file containing the folder hierarchy which is to be read
    Return
        levels, a dictionary which provides the levels of the folder hierarchy to be created
    '''
    
    # open and read the files
    file = open(filepath, 'r')
    all_text = file.readlines()
    
    # check if the file is correctly formatted
    if any(not s.strip() for s in all_text) == 0:
        raise Exception('Please separate levels of folder hierarchy by a blank line in ' + filepath + '.')
    if not all_text[0].strip():
        raise Exception('Please put the root of the folder hierarchy on the first line of ' + filepath + '.')
    if all_text[1].strip():
        raise Exception('Please ensure that the root of the folder hierarchy is a single directory in ' + filepath + '.')

    
    # initialize the levels dictionary, the line number, and level of hierarchy
    levels = {}
    line = 0
    level = 1
    
    # read each block of consecutive lines of text and add its words to the level of hierarchy
    while line < len(all_text):
        line_words = [l.strip() for l in all_text[line].split()]
        if line_words:
            if level not in levels.keys():
                levels[level] = [line_words]
            else:
                levels[level].append(line_words)
        else:
            level += 1
        line += 1
    
    return levels

def create_dir_structure(file_dir, levels):
    '''
    Given
        file_dir, the directory containing the files and where to place the folder hierarchy
        levels, dictionary which provides the levels of the folder hierarchy being created
    Populate the folder hierarchy within file_dir (all empty folders to start)
    '''
    
    # cd into the directory specified by file_dir
    file_path = os.path.join(expanduser('~'), file_dir)
    os.chdir(file_path)
    
    # initialize dictionary of all new directory paths to be created at each level with the "root", then create the "root"
    paths_dict = {1: levels[1][0]}
    if not os.path.exists(paths_dict[1][0]):
        os.mkdir(paths_dict[1][0])
    
    # iterate through the "lower" levels of the new folder hierarchy, and populate all new directory paths to be created
    max_level = len(levels)
    for level in range(2, max_level+1):
        paths_dict[level] = [os.path.join(parent_path, level_ele[0]) for parent_path in paths_dict[level-1] for level_ele in levels[level]]
        for path in paths_dict[level]:
            if not os.path.exists(path):
                os.mkdir(path)
            
def rearrange_files(file_dir, levels):
    '''
    Given
        file_dir, the directory containing the files and where to place the folder hierarchy
        levels, dictionary which provides the levels of the folder hierarchy being created
    Move the files into the appropriate folder at the bottom of the hierarchy
    '''
    
    # find the "deepest" level of the hierarchy first
    max_level = len(levels)
    
    # step one level back, find all the files in file_dir matching this level for a specific subdirectory and move files
    for level_ele in levels[max_level-1]:
        os.chdir(file_dir)
        for max_level_ele in levels[max_level]:
            if len(max_level_ele) > 1:
                files_to_move = [f for f in os.listdir('.') if max_level_ele[1] in f and level_ele[0] in f]
            else:
                files_to_move = [f for f in os.listdir('.') if max_level_ele[0] in f and level_ele[0] in f]

            for file in files_to_move:
                os.rename(os.path.join('.', file), os.path.join(file_dir, levels[1][0][0], level_ele[0], max_level_ele[0], file))

# Check for specification of this script and two arguments, then if the first argument is a text file
# Then read the input file, populate the folder hierarchy and find and move the files
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Please specify command in the following format [script file] [input file] [directory with files to move]')
    elif not sys.argv[1].endswith('.txt'):
        print('Input file not in .txt format.')
    elif sys.argv[2].endswith('.txt'):
        print('Input file must be the first argument.')
    else:
        try:
            levels = read_input(sys.argv[1])
            home = expanduser("~")
            start_dir = os.path.join(home, sys.argv[2])
            create_dir_structure(start_dir, levels)
        except Exception as e:
            print(e)
        else:
            rearrange_files(start_dir, levels)