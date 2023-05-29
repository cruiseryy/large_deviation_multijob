#--------------------------------------------------------------------------------------------#
# A LDS (Large Deviation Sampler) class is defined here to execute the experiments           #
# version V0.3 by xp53, May 29 2023                                                          #
#--------------------------------------------------------------------------------------------#

import numpy as np
import xarray as xr
import os
import bisect
import yaml
import subprocess
from bc_retriever import bc_tool
from time import time
from datetime import datetime, timedelta

class LDS:
    def __init__(self, 
                 path = './',
                 ref = 10, 
                 N = 10, 
                 K = 1, 
                 T = 18,
                 ic_pool = 5,
                 bc_pool = 5) -> None:
        np.random.seed()
        # path of working directory
        self.path = path 
        # a rescaling coefficient for the weights
        self.K = K 
        # number of trajectories
        self.N = N
        # T = number of dts
        self.T = T
        # to store intermediate variables:
        self.weights = np.zeros([self.N, self.T])
        self.R = np.zeros([self.T,])
        # parent[jc][i+1] = jp, at time step t+1 the jc^th traj's parent is jp
        self.parent = [[0]*self.T for _ in range(self.N)]
        self.bc_record = [[0]*self.T for _ in range(self.N)]
        # baseline value per unit time for computing deficit
        self.ref = ref
        # traj and sub info 
        self.ic_pool = ic_pool 
        self.bc_pool = bc_pool
        
        return
    
    def mkfolder(self) -> None:
        process = subprocess.Popen([self.path + '/mkfolder.sh'] + [str(self.N-1), self.path])
        process.wait()
        return 
    
    def get_ymd(self, i, icy):
        start = str(icy) + '-12-01'
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = start_date + timedelta(days=5*i)
        return end_date.strftime('%Y-%m-%d')

    def run(self) -> None:

        with open('timer.yml', 'r') as tmp_file:
            tmp_data = yaml.safe_load(tmp_file)
            self.timer = tmp_data['timer']
            
        if self.timer == 0:
            self.mkfolder()
            self.ic = [[0]*self.T for _ in range(self.N)]
            np.savetxt(self.path + '/vars/ic.txt', self.ic)
            np.savetxt(self.path + '/vars/path.txt', self.path)
            for j in range(self.N):
                self.ic[j][0] = np.random.randint(self.ic_pool) + 1981
                source = self.path + '/wrflowinp/wrflowinp_' + str(self.ic[j][0])
                dest = self.path + '/traj/' + '{:02d}'.format(j) + '/wrflowinp_d01'
                cmd = 'cp -f ' + source + ' ' + dest
                os.system(cmd)
                self.prev.append(self.path + '/traj/' + '{:02d}'.format(j) + '/wrfrst_d01_' + str(self.ic[j][0]-1) + '-12-01_00:00:00')
        else:
            self.var_load()
            self.eval(self.timer)
            self.resample(self.timer)
            self.perturb(self.timer)
        
        self.var_record()
        self.update(self.timer)

        with open('timer.yml', 'w') as tmp_file:
            tmp_data['timer'] += 1
            yaml.dump(tmp_data, tmp_file)
        return
    
    def var_load(self):
        self.prev = np.loadtxt(self.path + '/vars/prev.txt')
        self.ic = np.loadtxt(self.path + '/vars/ic.txt')
        self.bc_record = np.loadtxt(self.path + '/vars/bc_record.txt')
        self.parent = np.loadtxt(self.path + '/vars/topo.txt')
        self.R = np.loadtxt(self.path + '/vars/R.txt')
        self.weights = np.loadtxt(self.path + '/vars/weights.txt')
        return

    def var_record(self):
        np.savetxt(self.path + '/vars/prev.txt', self.prev)
        np.savetxt(self.path + '/vars/ic.txt', self.ic)
        np.savetxt(self.path + '/vars/bc_record.txt', self.bc_record)
        np.savetxt(self.path + '/vars/topo.txt', self.parent)
        np.savetxt(self.path + '/vars/R.txt', self.R)
        np.savetxt(self.path + '/vars/weights.txt', self.weights)
        return

    def update(self, i) -> None:
        for j in range(self.N):
            rb = np.random.randint(self.bc_pool)
            self.bc_record[j][i] = rb 
            bc_tool(self.ic[j][i], j, i, rb, self.path)
        np.savetxt(self.path + '/vars/bc_record.txt', self.bc_record)
        for k in range(4):
            self.slave_pbs(k)
        return
    
    def slave_pbs(self, k):
        file0 = self.path + 'slave0.pbs'
        with open(file0, 'r') as file:
            lines = file.readlines()
        lines[5] = lines[5].replace('0', str(k))  # Line 6
        lines[6] = lines[6].replace('0', str(k))  # Line 7
        lines[7] = lines[7].replace('0', str(k))  # Line 8
        lines[11] = lines[11].replace('0', str(k))  # Line 12
        tmpfile = self.path + 'slave.pbs'
        with open(tmpfile, 'w') as file:
            file.writelines(lines)
        subprocess.run(['qsub', 'slave.pbs'])
        return

    def eval(self, i) -> None:
        for j in range(self.N):
            start_file = self.prev[j]
            end_file = self.path + '/traj/' + '{:02d}'.format(j) + '/wrfrst_d01_' + self.get_ymd(i+1, self.ic[j][i]-1) + '_00:00:00'
            # print('starting file is' + start_file)
            # print('\n ending file is ' + end_file)
            start = xr.open_dataset(start_file)
            end = xr.open_dataset(end_file)
            print('this is traj {} at time step {}'.format(j, i))
            prcp_diff = np.sum(end['RAINNC'] - start['RAINNC'])
            prcp_diff /= (start['RAINNC'].shape[1] * start['RAINNC'].shape[2])
            print((self.K, self.ref, prcp_diff))
            self.weights[j, i] = np.exp(self.K * (self.ref*5 - prcp_diff))

        print(self.weights[:, i])
        self.R[i] = np.mean(self.weights[:, i])
        print(self.R[i])
        self.weights[:, i] /= self.R[i]
        return
    
    def resample(self, i) -> None:
        # the cdf estimated using weights is used to draw new trajs
        tmpcdf = np.zeros([self.N,])
        tmpcdf[0] = self.weights[0, i]
        for j in range(1, self.N):
            tmpcdf[j] = tmpcdf[j-1] + self.weights[j, i]
        tmpcdf /= tmpcdf[-1]
        # repeat the sampling for N times
        for j in range(self.N):
            idx = bisect.bisect(tmpcdf, np.random.rand())
            self.parent[j][i+1] = idx
            self.ic[j][i+1] = self.ic[idx][i]
            source = self.path + '/traj/' + '{:02d}'.format(idx) + '/wrfrst_d01_' + self.get_ymd(i+1, self.ic[idx][i]-1) + '_00:00:00'
            tmp_filename = source[-30:]
            dest = self.path + '/traj/' + '{:02d}'.format(j) + '/' + tmp_filename
            cmd = 'cp -f ' + source + ' ' + dest
            os.system(cmd)
            source2 = self.path + '/wrflowinp/wrflowinp_' + str(self.ic[j][i+1])
            dest2 = self.path + '/traj/' + '{:02d}'.format(j) + '/wrflowinp_d01'
            cmd2 = 'cp -f ' + source2 + ' ' + dest2
            os.system(cmd2)
            self.prev[j] = dest
        return
    
    def perturb(self, i):
        pause = 1
        return 
    
    def save_var(self):
        
        np.savetxt('ic.txt', self.ic)
        np.savetxt('topo.txt', self.parent)
        np.savetxt('weights.txt', self.weights)
        np.savetxt('bc_record.txt', self.bc_record)

        return

if __name__ == "__main__":
    
    para = yaml.safe_load(open('config.yml'))
    sampler = LDS(**para)
    sampler.run()
    pause = 1
