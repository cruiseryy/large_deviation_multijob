import xarray as xr
import numpy as np
import subprocess
from time import time

def bc_tool(icy, j, i, rb, path) -> None:

    src = path + '/wrf_bc/' + str(i) + '/' + 'bc_' + str(icy)
    dest = path + '/traj/' + '{:02d}'.format(j) + '/wrfbdy_d01'
    new_bc = path + '/wrf_bc/' + str(i) + '/' + 'bc_' + str(1981+rb)

    data0 = xr.open_dataset(new_bc)
    data1 = xr.open_dataset(src)

    var_ls = list(data0.keys())
    for i_, k in enumerate(var_ls):
        if i_ <= 2: continue
        data1[k] = data0[k]

    data1.to_netcdf(dest)

    return 


if __name__ == '__main__':

    path = '/Volumes/SamsungT7/work/wrf_demo'
    N = 10
    T = 7
    bc_pool = 5

    process = subprocess.Popen([path + '/mkfolder.sh'] + [str(N-1), str(T-1)])
    process.wait()

    ic = [0]*N
    bc = [[0]*T for _ in range(N)]

    for j in range(N):
        ic[j] = np.random.randint(bc_pool) + 1981
    
    for i in range(7):
        processes = []
        t1 = time()
        for j in range(N):

            rb = np.random.randint(5)

            bc_tool(ic[j], j, i, rb, path)

            process = subprocess.Popen([path + '/tmp.sh'] + [str(j), str(i), str(ic[j]), path])
            processes.append(process)
            # pause = 1

        flag = 1

        for sp in processes: 
            if sp.wait() != 0:
                flag = 0

        t2 = time()
        print(t2-t1)
        pause = 1

        # t1 = time()
        # for i in range(10):
        #     rb = np.random.randint(5)
        #     bc_tool(ic[i], i, j, rb)
        #     process = subprocess.Popen(['./tmp.sh'] + [str(i), str(j), str(ic[i])])
        #     process.wait()
        #     pause = 1
        # flag = 1
        # t2 = time()
        # print(t2-t1)
        # pause = 1