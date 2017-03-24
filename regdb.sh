#!/bin/bash
filename="$1"
read pawd
export PGPASSWORD=$pawd
while read -r line
do
    name="$line"
    psql -U rc_reg_datastore_readonly -d rc_reg_datastore -h f7oddataregb1.statcan.gc.ca -c "copy (select count(*) from \"$name\") to stdout;"  >> /tmp/in_count.csv
    #echo "Name read from file - $name"
done < "$filename"

