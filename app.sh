#!/usr/bin/env bash
sudo kill $(sudo ps aux | grep wx_server | awk '{print $2}')
sudo -b nohup /home/fanzfeng/anaconda3/bin/python wx_server.py 80 >> nohup.out
