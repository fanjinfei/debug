#!/bin/sh

DIALOG=${DIALOG=dialog}
tempfile=`tempfile 2>/dev/null` || tempfile=/tmp/test$$
trap "rm -f $tempfile" 0 1 2 5 15

$DIALOG --title "My input box" --clear \
        --inputbox "Hi, this is a sample input box\n
Try entering your name below:" 16 51 2> $tempfile

retval=$?

case $retval in
  0)
    echo "Input string is `cat $tempfile`";;
  1)
    echo "Cancel pressed.";;
  255)
    if test -s $tempfile ; then
      cat $tempfile
    else
      echo "ESC pressed."
    fi
    ;;
esac

