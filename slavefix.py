#--------------------------------------------------------------------------------------------#
# A LDS (Large Deviation Sampler) class is defined here to execute the experiments           #
# version V0.2 by xp53, May 29 2023                                                          #
#--------------------------------------------------------------------------------------------#

import numpy as np
import yaml
import subprocess
import sys

class lds_slave:

    def __init__(self, k) -> None:
        # self.k = int(k)
        self.k = 3
        tmp_path_file = '/scratch/users/nus/xp53/lds_multijob/large_deviation_multijob/vars/path.txt'
        with open(tmp_path_file, 'r') as file:
            self.path = file.readline()
        print(self.path)
        # with open('timer.yml', 'r') as tmp_file:
        #     self.tmp_data = yaml.safe_load(tmp_file)
        #     self.timer = self.tmp_data['timer']
        # print(self.timer)
        self.timer = 1 
        return
    
    def var_load(self):
        tmp_prev_file = self.path + '/vars/prev.txt'
        with open(tmp_prev_file, 'r') as file:
            lines = file.readlines()
        self.prev = [line.strip() for line in lines]
        self.ic = np.loadtxt(self.path + '/vars/ic.txt').astype(int)
        self.bc_record = np.loadtxt(self.path + '/vars/bc_record.txt').astype(int)
        self.parent = np.loadtxt(self.path + '/vars/topo.txt').astype(int)
        self.R = np.loadtxt(self.path + '/vars/R.txt')
        self.weights = np.loadtxt(self.path + '/vars/weights.txt')
        pause = 1
        return
    
    def update(self):
        self.var_load()
        processes = []
        for j in range(32):
            rj = self.k*32 + j 
            if rj != 122: continue
            process = subprocess.Popen([self.path + '/tmp.sh'] + [str(rj), str(self.timer), str(self.ic[rj][self.timer]-1), self.path])
            processes.append(process)

        # if self.k == 3:
        #     with open('timer.yml', 'w') as tmp_file:
        #         self.tmp_data['timer'] += 1
        #         yaml.dump(self.tmp_data, tmp_file)
                
        flag = 1
        for sp in processes:
            if sp.wait() != 0:
                flag = 0 
        print('traj {} from chunk {} is fixed'.format(rj, self.k))
        return 
        
if __name__ == '__main__':
    # print(sys.argv[1])
    # print(type(sys.argv[1]))
    # ss = lds_slave(sys.argv[1])
    ss = lds_slave()
    ss.update()

