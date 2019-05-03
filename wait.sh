#!/bin/bash

while [ -e /proc/$1 ]; do 
  sleep 5; 
  #cat /proc/$1/status | grep VmSize")
  #ps -eo pid,lstart,cmd |grep R
done

date > $2
