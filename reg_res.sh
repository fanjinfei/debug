#!/bin/bash
filename="$1"
read pawd
export PGPASSWORD=$pawd
echo $pawd
#psql -U rc_reg_user -d rc_reg -h f7oddataregb1.statcan.gc.ca  -c "copy (select id  from package where type='inventory') to stdout;" > inventory_res.csv
while read -r line
do
    name="$line"
    psql -U rc_reg_user -d rc_reg -h f7oddataregb1.statcan.gc.ca -c "copy (select id from resource where package_id='$name') to stdout;" >> /tmp/in_dat.csv
    #echo "Name read from file - $name"
    #echo "$cmd"
    #$("$cmd")
done < "$filename"

