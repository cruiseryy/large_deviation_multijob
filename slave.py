#--------------------------------------------------------------------------------------------#
# A LDS (Large Deviation Sampler) class is defined here to execute the experiments           #
# version V0.2 by xp53, May 29 2023                                                          #
#--------------------------------------------------------------------------------------------#

import numpy as np
import xarray as xr
import os
import bisect
import yaml
import subprocess
import sys
from bc_retriever import bc_tool
from time import time
from datetime import datetime, timedelta

class lds_slave:

    def __init__(self, k) -> None:
        self.k = int(k)
        return
    
    def var_load(self):
        self.prev = np.loadtxt('/vars/prev.txt')
        self.ic = np.loadtxt('/vars/ic.txt')
        self.bc_record = np.loadtxt('/vars/bc_record.txt')
        self.parent = np.loadtxt('/vars/topo.txt')
        self.R = np.loadtxt('/vars/R.txt')
        self.weights = np.loadtxt('/vars/weights.txt')
        return
    
    def update(self):
        with open('timer.yml', 'r') as tmp_file:
            tmp_data = yaml.safe_load(tmp_file)
            self.timer = tmp_data['timer']
        self.path = np.loadtxt('/vars/path.txt')
        self.var_load()
        processes = []
        for j in range(32):
            process = subprocess.Popen([self.path + '/tmp.sh'] + [str(j), str(self.timer), str(self.ic[j][self.timer]-1), self.path])
            processes.append(process)
        flag = 1
        for sp in processes:
            if sp.wait() != 0:
                flag = 0 
        print('all subprocesses from chunk {} done'.format(self.k))
        return 
        
if __name__ == '__main__':
    ss = lds_slave(sys.argv[1])
    # print(ss.k)
    # print(type(ss.k))
    ss.update()

