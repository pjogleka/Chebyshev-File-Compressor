import argparse
from argparse import RawTextHelpFormatter
from compress import compress
from decompress import decompress
from read_file import read_file
import os


def get_file_list(input_path):
    
    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = [os.path.join(input_path, file) for file in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, file))]
    return files


def validate_process(process):

    if process != "comp" and process != "decomp":
        raise ValueError("Invalid process")    


def validate_c_level(c_level):
    
    if c_level not in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        raise ValueError("Invalid C level")
    
        
def validate_path(input_path):
    if not os.path.isfile(input_path) and not os.path.isdir(input_path):
        raise ValueError("Invalid input path")


def validate_comp(input_path):
    files = get_file_list(input_path)
    for file in files:
        x = read_file(input_path)
        if x.file_name[:4] == "comp":
            raise ValueError("File already compressed")
        try:
            x.get_file_type()
        except:
            raise ValueError("File type 'CF' or 'FP' must appear in file name")


def validate_decomp(input_path):
    files = get_file_list(input_path)
    for file in files:
        x = read_file(input_path)
        if x.file_name[:4] != "comp":
            raise ValueError("File name did not start with 'comp'")
        try:
            x.get_file_type()
        except:
            raise ValueError("File type 'CF' or 'FP' must appear in file name")


def validate():
    
    args = parse_args()
    
    validate_process(args.process)
    
    if args.c_level:
        validate_c_level(args.c_level)
    
    validate_path(args.input_path)

    if args.process == "comp":
        validate_comp(args.input_path)
    
    if args.process == "decomp":
        validate_decomp(args.input_path)
            
    return args


def parse_args():
    
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("input_path", type=str, help="Path to file or directory being processed")
    parser.add_argument("process", type=str, help="'comp' or 'decomp'")
    parser.add_argument("-d", "--out_dir", type=str, help="Name of output directory")
    parser.add_argument("-c", "--c_level", type=int, help="Level of compression (1=low, 9=high). Accuracy is lost with higher compression")
    return parser.parse_args()


def main():

    try:
        args = validate()
    except Exception as e:
        print(f"Caught exception: {e}")
        return None
    
    if args.out_dir and not os.path.isdir(args.out_dir):
        os.mkdir(args.out_dir)
    if not args.c_level:
        args.c_level = 3
    
    files = get_file_list(args.input_path)
    if args.process == "comp":
        for file in files:
            compress(file, args.c_level, args.out_dir)
    elif args.process == "decomp":
        for file in files:
            decompress(file, args.out_dir)


if __name__ == "__main__":
    main()