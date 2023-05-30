import os 

# '/data/projects/11002298/long/xpwrf/1981/wrfbdy_d01'
source = '/data/projects/11002298/long/xpwrf/'
dest = '/scratch/users/nus/xp53/lds_multijob/large_deviation_multijob/'

for yy in range(1981, 2021):
    source2 = source + str(yy) + '/wrfrst_d01_' + str(yy-1) + '-12-01_00:00:00'
    dest2 = dest + 'wrf_ic/wrfrst_d01_' + str(yy-1) + '-12-01_00:00:00'
    cmd2 = 'cp -f ' + source2 + ' ' + dest2
    os.system(cmd2)

    source3 = source + str(yy) + '/wrflowinp_d01'
    dest3 = dest + 'wrflowinp/wrflowinp_' + str(yy)
    cmd3 = 'cp -f ' + source3 + ' ' + dest3
    os.system(cmd3)
