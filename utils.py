import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import os
# from matplotlib import pyplot as plt
# import cartopy.crs as ccrs

class ReadRainfall:
    def __init__(self, n = 32, path = 'path.txt', T = 5) -> None:
        self.n = n 
        with open(path, 'r') as file:
            self.path = file.readline()
        print(self.path)
        self.ic = np.loadtxt(self.path + '/vars/ic.txt').astype(int)
        self.bc_record = np.loadtxt(self.path + '/vars/bc_record.txt').astype(int)
        self.parent = np.loadtxt(self.path + '/vars/topo.txt').astype(int)
        self.R = np.loadtxt(self.path + '/vars/R.txt')
        self.weights = np.loadtxt(self.path + '/vars/weights.txt')
        self.T = T
        pause = 1
        return
    
    def get_ymd(self, i, icy):
        start = str(icy) + '-12-01'
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = start_date + timedelta(days=i)
        return end_date.strftime('%Y-%m-%d')
    
    def read_data(self):
        tmp_pre = 'wrfrst_d01_'
        tmp_suf = '_00:00:00'
        
        for j in range(self.n):
            rain = np.zeros([self.T*6, 120*160])
            mark = 0
            for t in range(self.T):
                for i in range(6):
                    tmpymd = self.get_ymd(i = t*5 + i, icy = self.ic[j, t]-1)
                    tmpfile = self.path + '/traj/' + '{:02d}'.format(j) + '/' + tmp_pre + tmpymd + tmp_suf
                    print(tmpfile)
                    if not os.path.exists(tmpfile):
                        filler = np.ones([120*160,]) * -999
                        rain[mark, :] = filler
                        mark += 1
                        continue
                    tmp_rain = xr.open_dataset(tmpfile)['RAINNC'][0,:,:].to_numpy()
                    tmp_rain_flat = tmp_rain.reshape([120*160, ])
                    rain[mark, :] = tmp_rain_flat
                    mark += 1
            
            np.savetxt(self.path + '/output/rainfall_' + str(j) +'.txt', rain)

            # rain_flat = tmp_rain.reshape(tmp_rain.shape[0], -1)
            # data_flat = np.loadtxt(dest)
            # data = data_flat.reshape(data_flat.shape[0], 120, 160)

            
        return
    
    # def read_data2(self):
    #     tmp_pre = 'wrfrst_d01_'
    #     tmp_suf = '_00:00:00'

    #     for j in range(self.n):

    #         tmp_path = self.path + 'traj/' + '{:02d}'.format(j) + '/' + tmp_pre 

    #         tmp_rain = np.zeros([9, 120, 160])
    #         ii = [1, 2, 3, 4, 5, 6, 6, 7, 8]

    #         for i in range(9):

    #             idx = ii[i]

    #             if i < 6: 
    #                 tmp_file = tmp_path + str(self.ic[j, 0]-1) + '-12-' + '{:02d}'.format(idx) + tmp_suf
    #             else:
    #                 tmp_file = tmp_path + str(self.ic[j, 1]-1) + '-12-' + '{:02d}'.format(idx) + tmp_suf

    #             tmp_rain[i, :, :] = xr.open_dataset(tmp_file)['RAINNC'][0,:,:]


    #         rain_flat = tmp_rain.reshape(tmp_rain.shape[0], -1)
    #         np.savetxt(self.path + 'traj/rainfall_' + str(j) +'.txt', rain_flat)

    #     return
    

if __name__ == "__main__":
    test = ReadRainfall(n = 128, path = '/scratch/users/nus/xp53/lds_multijob/large_deviation_multijob/vars/path.txt', T = 9)
    test.read_data()