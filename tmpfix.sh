#!/bin/bash

#--------------------------------------------------------------------------------------------#
# this a shell script that prepares BCs and ICs for WRF simulation                           #
# version V0.3 by xp53, May 29 2023                                                          #
# contact me via xp53@ + cornell.edu or nus.edu.sg                                           #
#--------------------------------------------------------------------------------------------#
# $1 -> the ith traj
# $2 -> the jth sub interval
# $3 -> the IC year yyyy
# $4 -> the working directory
i=$(printf "%02d" $1)
# j=$(printf "%02d" $2)
j=$2
ic_yy=$3
rund=$4/traj/$i/
fd=5

cd $rund
cp $4/namelist0 namelist.input

chmod 777 namelist.input
prefix="wrfrst_d01_"

if [ "$j" -eq 0 ]; then
    echo "The first argument is equal to 0."

    # set start as yyyy-mm-dd-hh = IC year-12-01-00
    sed -i "6s/yrs/$ic_yy/g" namelist.input
    sed -i "7s/11/12/g" namelist.input
    sed -i "8s/26/01/g" namelist.input
    tmpin="${prefix}${ic_yy}-12-01_00:00:00"
    cp $4/wrf_ic/wrfrst_d01_${ic_yy}-12-01_00:00:00 $tmpin

    # set end as yyyy-mm-dd-hh = IC year-12-06-00
    sed -i "10s/yre/$ic_yy/g" namelist.input
    # sed -i "11s/07/12/g" namelist.input
    sed -i "12s/01/06/g" namelist.input
    sed -i "13s/22/00/g" namelist.input
    sed -i "18s/false/true/g" namelist.input

    # tmpout="${prefix}${ic_yy}-12-06_00:00:00"
    # cp $tmpin $tmpout # this line is for testing, drop this later

else
    echo "The first argument is not equal to 0."

    base_ymd="$ic_yy-12-01"
    # get yyyy-mm-dd part and compute end time by adding 5 days
    gap1=$((fd * j))
    gap2=$((fd * (j+1)))

    start_ymd=$(date -d "$base_ymd + $gap1 days" +"%Y-%m-%d")
    end_ymd=$(date -d "$base_ymd + $gap2 days" +"%Y-%m-%d")

    sy=${start_ymd:0:4}
    sm=${start_ymd:5:2}
    sd=${start_ymd:8:2}
    ey=${end_ymd:0:4}
    em=${end_ymd:5:2}
    ed=${end_ymd:8:2}
    
    echo $sy-$sm-$sd
    echo $ey-$em-$ed

    # set start time as time stamp of the last wrfrst file
    sed -i "6s/yrs/$sy/g" namelist.input
    sed -i "7s/11/$sm/g" namelist.input
    sed -i "8s/26/$sd/g" namelist.input
    # tmpin="wrfrst_d01_${start_ymd}_00:00:00"

    # set end time as (start time + 5 day)
    sed -i "10s/yre/$ey/g" namelist.input
    sed -i "11s/12/$em/g" namelist.input
    sed -i "12s/01/$ed/g" namelist.input
    sed -i "13s/22/00/g" namelist.input
    sed -i "18s/false/true/g" namelist.input

    # tmpout="wrfrst_d01_${end_ymd}_00:00:00"
    # cp $tmpin $tmpout # this line is for testing, drop this later

fi

echo "file modification done"
mpirun -np 128 ./wrf.exe
echo "wrf run done"

# sleep 10
# echo sleepppppptesttesttest
