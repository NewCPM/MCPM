import sys
import numpy as np


# File with short functions used in different parts of the code.
# Contains:
# - pixel_list_center()
# - load_matrix_xy()
# - save_matrix_xy()
# - read_true_false_file()

def pixel_list_center(center_x, center_y, half_size):
    """Return list of pixels centered on (center_x,center_y) 
    [rounded to nearest integer] and covering 
    n = 2*half_size+1 pixels on the side. The output shape is (n^2, 2)"""
    int_x = int(center_x + 0.5)
    int_y = int(center_y + 0.5)
    return np.mgrid[(int_x-half_size):(int_x+half_size+1), 
                    (int_y-half_size):(int_y+half_size+1)].reshape(2, -1).T

def load_matrix_xy(file_name, data_type='float'):
    """reads file with matrix in format like:
    0 0 123.454
    0 1 432.424
    ...
    into numpy array"""
    parser = {'TRUE': True, 'FALSE': False}
    table_as_list = []
    with open(file_name) as infile:
        for line in infile.readlines():
            if line[0] == '#':
                continue
            data = line.split()
            if len(data) != 3:
                raise ValueError("incorrect line read from file {:} : {:}".format(file_name, line[:-1]))
            x = int(data[0])
            y = int(data[1])
            
            if data_type == 'float':
                value = float(data[2])
            elif data_type == 'boolean':
                value = parser[data[2].upper()]
            else:
                raise ValueError('Unknown data_type in load_matrix_xy()')

            if len(table_as_list) < x + 1:
                for i in range(x+1-len(table_as_list)):
                    table_as_list.append([])
            if len(table_as_list[x]) < y + 1:
                for i in range(y+1-len(table_as_list[x])):
                    table_as_list[x].append(None)
            
            table_as_list[x][y] = value

    return np.array(table_as_list)
    
def save_matrix_xy(matrix, file_name, data_type='float'):
    """saves numpy array (matrix) in format like:
    0 0 123.454
    0 1 432.424
    ...
    """
    with open(file_name, 'w') as out_file:
        if data_type == 'float':
            for (index, value) in np.ndenumerate(matrix):
                out_file.write("{:} {:} {:.8f}\n".format(index[0], index[1], value))
        elif data_type == 'boolean':
            parser = {1: "True", 0: "False"}
            for (index, value) in np.ndenumerate(matrix):
                out_file.write("{:} {:} {:}\n".format(index[0], index[1], parser[value]))
        else:
            raise ValueError('save_matrix_xy() - unrecognized format')
        
def read_true_false_file(file_name):
    """Reads file with values True or False into a boolean numpy array.
    To save such a file, just use:
    np.savetxt(FILE_NAME, BOOL_ARRAY, fmt='%r')
    """
    parser = {'TRUE': True, 'FALSE': False}
    out = []
    with open(file_name) as in_file:
        for line in in_file.readlines():
            out.append(parser[line[:-1].upper()])
    return np.array(out)
