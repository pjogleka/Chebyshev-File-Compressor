from read_file import read_file
from comp_calc import normalize
from fmt import fmt
import numpy as np
import itertools


def expand(alt_vals_norm, decomp):
    '''Return exponentiated Chebyshev expansion of coefficients'''
    return np.exp(np.polynomial.chebyshev.chebval(alt_vals_norm, np.array(decomp).astype(float)))


def line_fmt(in_line, alt_vals, file_type):
    
    if in_line[0] == "*":
        out_line = np.array(in_line[1:]).astype(float)                
    elif in_line[0][0] == "x":
        repeats = np.repeat(float(in_line[1]), int(in_line[0][1:]))
        alt_vals_norm = normalize(alt_vals[int(in_line[0][1:]):])
        exp_vals = expand(alt_vals_norm, in_line[2:])
        out_line = np.concatenate((repeats, exp_vals))  
    else:
        alt_vals_norm = normalize(alt_vals)
        out_line = expand(alt_vals_norm, in_line)
    out_line = fmt(out_line, file_type)
    return out_line


def decompress(file_path, out_dir=None):

    x = read_file(file_path, decomp=True)
    x.get_footer()
    x.get_file_type()
    
    if out_dir:
        out_name = f'{out_dir}/de{x.file_name}'
    else:
        out_name = f'de{x.file_name}'
    
    with open(out_name, 'w') as out, open(file_path) as comp:
            
            out.write(x.header + "\n")

            for in_line in itertools.islice(comp, 6, 6 + np.size(x.lat_vals)*np.size(x.lon_vals)):
                out_line = line_fmt(in_line.split(), x.alt_vals, x.file_type)
                out.write(out_line)
            
            out.write(x.footer)
    
    print(f"Wrote decompressed file de{x.file_name}")