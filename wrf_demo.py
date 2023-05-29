#--------------------------------------------------------------------------------------------#
# A LDS (Large Deviation Sampler) class is defined here to execute the experiments           #
# version V0.2 by xp53, Apr 17 2023                                                          #
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
        # to record the current timestep
        self.timer = 0
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

        # pause = 1
    
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
        self.mkfolder()
        self.ic = [[0]*self.T for _ in range(self.N)]
        self.prev = []
        for j in range(self.N):
            self.ic[j][0] = np.random.randint(self.ic_pool) + 1981
            source = self.path + '/wrflowinp/wrflowinp_' + str(self.ic[j][0])
            dest = self.path + '/traj/' + '{:02d}'.format(j) + '/wrflowinp_d01'
            cmd = 'cp -f ' + source + ' ' + dest
            os.system(cmd)
            self.prev.append(self.path + '/traj/' + '{:02d}'.format(j) + '/wrfrst_d01_' + str(self.ic[j][0]-1) + '-12-01_00:00:00')
        while self.timer < self.T:
            self.update(self.timer)
            self.eval(self.timer)
            if self.timer == self.T - 1:
                break
            self.resample(self.timer)
            self.perturb(self.timer)
            self.save_var()
            print('interval {} done'.format(self.timer))
            self.timer += 1
        
        return

    def update(self, i) -> None:
        processes = []
        for j in range(self.N):
            rb = np.random.randint(self.bc_pool)
            self.bc_record[j][i] = rb 
            bc_tool(self.ic[j][i], j, i, rb, self.path)
            process = subprocess.Popen([self.path + '/tmp.sh'] + [str(j), str(i), str(self.ic[j][i]-1), self.path])
            processes.append(process)
        flag = 1
        for sp in processes:
            if sp.wait() != 0:
                flag = 0 
        print('all subprocesses done')
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
