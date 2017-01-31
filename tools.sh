#!/bin/bash
filename="$1"
while read -r line
do
    name="$line"
    while read -r line2
    do
       name2="$line2"
       cmd="abin/xxx $name $name2"
       #echo "Name read from file - $name"
       echo "$cmd"
       $("$cmd")
    done < "$name"
done < "$filename"
