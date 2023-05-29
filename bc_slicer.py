import numpy as np
import xarray as xr

# /data/projects/11002298/long/sgwrf/1981/wrfbdy_d01
pre = '/data/projects/11002298/long/xpwrf/'
dest = '/home/users/nus/xp53/wrf_demo/wrf_bc/' 

for yr in range(1981, 1990):
    file = pre + str(yr) + '/wrfbdy_d01'
    data = xr.open_dataset(file)
    tmpstr = str(yr-1) + '-12-01_00:00:00'
    cur = np.where(data['Times'] == bytes(tmpstr, encoding='utf-8'))[0][0]
    for i in range(18):
        tdata1 = data.isel(Time=slice(cur,cur+41))
        tmpdest = dest + str(i) + '/bc_' + str(yr)
        tdata1.to_netcdf(tmpdest)
        cur += 40
    
                         