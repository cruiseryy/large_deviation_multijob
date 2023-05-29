import numpy as np
import xarray as xr
# from matplotlib import pyplot as plt
# import cartopy.crs as ccrs

class ReadRainfall:
    def __init__(self, n = 32, path = '') -> None:
        self.n = n 
        self.path = path 
        self.ic = np.loadtxt(self.path + 'ic.txt').astype(int)
        # self.weights = np.loadtxt(self.path + 'weights.txt')
        self.parents = np.loadtxt(self.path + 'topo.txt').astype(int)
        pause = 1
        return
    
    def read_data(self):
        tmp_pre = 'wrfrst_d01_'
        tmp_suf = '_00:00:00'
        self.traj = np.zeros([self.n, 7])
        for j in range(self.n):
            tmp_rain = np.zeros([7, 120, 160])
            ii = 8
            cur = self.path + 'traj/' + '{:02d}'.format(j) + '/' + tmp_pre + str(self.ic[j, 1]-1) + '-12-' + '{:02d}'.format(ii) + tmp_suf
            
            ii -= 1
            while ii >=  1:
                if ii >= 6:
                    nex = self.path + 'traj/' + '{:02d}'.format(j) + '/' + tmp_pre + str(self.ic[j, 1]-1) + '-12-' + '{:02d}'.format(ii) + tmp_suf
                    self.traj[j, ii-1] = self.ic[j, 1]
                else:
                    nj = self.parents[j,1]
                    nex = self.path + 'traj/' + '{:02d}'.format(nj) + '/' + tmp_pre + str(self.ic[nj, 0]-1) + '-12-' + '{:02d}'.format(ii) + tmp_suf
                    self.traj[j, ii-1] = self.ic[nj, 0]
                tmp_rain[ii-1, :, :] = xr.open_dataset(cur)['RAINNC'][0,:,:] - xr.open_dataset(nex)['RAINNC'][0,:,:]
                cur = nex 
                ii -= 1
            rain_flat = tmp_rain.reshape(tmp_rain.shape[0], -1)
            # data_flat = np.loadtxt(dest)
            # data = data_flat.reshape(data_flat.shape[0], 120, 160)
            np.savetxt(self.path + 'traj/rainfall_' + str(j) +'.txt', rain_flat)
            pause = 1
        # fig = plt.figure()
        # ax = plt.axes(projection=ccrs.PlateCarree())
        # ax.coastlines(resolution='10m')
        # cmap = plt.get_cmap('Blues', 20)
        # tmp = xr.open_dataset(cur)
        # pmap = plt.scatter(tmp['XLONG'][0], tmp['XLAT'][0], c = tmp_rain[0,:,:], cmap=cmap)
        # cbar = plt.colorbar(pmap)
        # cbar.set_label('Annual Prcp (mm)')
            
        return
    
    def read_data2(self):
        tmp_pre = 'wrfrst_d01_'
        tmp_suf = '_00:00:00'

        for j in range(self.n):

            tmp_path = self.path + 'traj/' + '{:02d}'.format(j) + '/' + tmp_pre 

            tmp_rain = np.zeros([9, 120, 160])
            ii = [1, 2, 3, 4, 5, 6, 6, 7, 8]

            for i in range(9):

                idx = ii[i]

                if i < 6: 
                    tmp_file = tmp_path + str(self.ic[j, 0]-1) + '-12-' + '{:02d}'.format(idx) + tmp_suf
                else:
                    tmp_file = tmp_path + str(self.ic[j, 1]-1) + '-12-' + '{:02d}'.format(idx) + tmp_suf

                tmp_rain[i, :, :] = xr.open_dataset(tmp_file)['RAINNC'][0,:,:]


            rain_flat = tmp_rain.reshape(tmp_rain.shape[0], -1)
            np.savetxt(self.path + 'traj/rainfall_' + str(j) +'.txt', rain_flat)

        return
    

if __name__ == "__main__":
    test = ReadRainfall()
    # test.read_data()
    test.read_data2()