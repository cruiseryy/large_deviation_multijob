from netCDF4 import Dataset
from wrf import getvar
import xarray as xr

data_array = []
var_ = 'SMCREL'
for i in range(1, 7):
    ncfile = 'wrfrst_d01_1984-12-2' + str(i) + '_00:00:00'
    with xr.open_dataset(ncfile) as ds:
        rain = ds[var_]
        data_array.append(rain)
    pause = 1
data_array.append(rain)

concatenated_data = xr.concat(data_array, dim='Time')
concatenated_data.to_netcdf(var_ + '.nc') 

with xr.open_dataset(var_ + '.nc') as ds:
    tmprain = ds[var_]
    pause = 1
pause = 1