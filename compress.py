from read_file import read_file
from comp_calc import get_cheb_data
from fmt import fmt
import numpy as np
import os

def write(data, file_type, huff, flag, cheb_coeff):
    '''Format compressed data depending on flags'''
    if flag:
        line = "*" + fmt(data, file_type)
    elif huff[0] != 0:
        huff_flag = f"x{huff[0]} {huff[1]}"
        line = huff_flag + fmt(cheb_coeff, "FP")
    else:
        line = fmt(cheb_coeff, "FP")
    return line
        

def compress(file_path, c_level, out_dir=None, store=False):
    
    tol = {1:1, 2:2.5, 3:5, 4:7.5, 5:10, 6:12.5, 7:15, 8:17.5, 9:20}
    
    x = read_file(file_path)
    x.get_footer()
    x.get_file_type()
    
    if out_dir:
        out_name = f'{out_dir}/comp_{x.file_name}'
    else:
        out_name = f'comp_{x.file_name}'
    
    with open(out_name, 'w') as out:
        
        out.write(x.header + "\n")
        
        if store:
            cheb_coeff_arr = [[] for i in range(np.size(x.lat_vals)*np.size(x.lon_vals))]
            cheb_approx_arr = [[] for i in range(np.size(x.lat_vals)*np.size(x.lon_vals))]
            for i in range(np.size(x.lat_vals)*np.size(x.lon_vals)):
                huff, flag, cheb_coeff, cheb_approx = get_cheb_data(x.file_type, x.alt_vals, x.data[i], tol[c_level])
                line = write(x.data[i], x.file_type, huff, flag, cheb_coeff)
                out.write(line)
                cheb_coeff_arr[i] = cheb_coeff
                cheb_approx_arr[i] = cheb_approx
            return cheb_coeff_arr, cheb_approx_arr
        
        elif not store:
            for i in range(np.size(x.lat_vals)*np.size(x.lon_vals)):
                huff, flag, cheb_coeff, cheb_approx = get_cheb_data(x.file_type, x.alt_vals, x.data[i], tol[c_level])
                line = write(x.data[i], x.file_type, huff, flag, cheb_coeff)
                out.write(line)
                
        out.write(x.footer)

    if out_dir:
        comp = os.path.getsize(file_path) / os.path.getsize(f"{out_dir}/comp_{x.file_name}")
    else:
        comp = os.path.getsize(file_path) / os.path.getsize(f"comp_{x.file_name}")
        
    print(f"Wrote compressed file comp_{x.file_name}\nCompression ratio: {comp}")