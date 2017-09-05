
#!/bin/bash
source $HOME/.bashrc

if [ $(ps -ef |grep staging-portal |wc | awk '{ print $1}') != 7 ];  then  pkill -SIGKILL -f /var/www/html/venv/staging-portal/bin/gunicorn;  sleep 5; /var/www/html/venv/bin/gunicorn-staging-portal start;  fi

