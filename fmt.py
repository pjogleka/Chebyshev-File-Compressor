import numpy as np


def fmt(vec, fmt_type):
    
    if fmt_type == "CF":
        array_fmt = np.array(list(map('{:.5E}'.format, vec)))
        M = np.char.add("   ", array_fmt)
            
    elif fmt_type == "FP":
        array_fmt = np.array(list(map('{:.6f}'.format, vec)))
        M = np.char.add("  ", array_fmt)
        M = np.array([m[1:] if len(m) > 10 else m for m in M])
        
    line = str.join("", M) + "\n"
    
    return line