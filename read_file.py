import numpy as np
import os
import itertools


class read_file:
    
    def __init__(self, file_path, decomp=False):

        self.file_path = file_path
        self.file_name = os.path.basename(self.file_path)
        self.get_vals()
        if not decomp:
            self.get_data()
    
    
    def _get_header(self):
        
        with open(self.file_path) as file:
            self._headerlist = [next(file) for i in range(6)]
        self.header = "".join(self._headerlist)[:-1]
    
    
    def get_vals(self):
        '''Pull metadata (grid points) from file'''
        self._get_header()
        self.alt_vals = np.fromstring(self._headerlist[1], sep = ' ')
        self.lat_vals = np.fromstring(self._headerlist[3], sep = ' ')
        self.lon_vals = np.fromstring(self._headerlist[5], sep = ' ')
    
    
    def get_data(self):
        
        self.data = np.loadtxt(self.file_path, max_rows=np.size(self.lat_vals)*np.size(self.lon_vals), skiprows=6)
    
    
    def get_footer(self):

        self.footer = ""
        with open(self.file_path) as file:
            for line in itertools.islice(file, 6 + np.size(self.lat_vals)*np.size(self.lon_vals), None):
                self.footer += line
    
    
    def get_file_type(self):
        
        if "CF" in self.file_name:
            self.file_type = "CF"
        elif "FP" in self.file_name:
            self.file_type = "FP"