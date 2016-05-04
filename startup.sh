#!/bin/bash

while true; do
    python pucauto.py
    echo Restarting...
    killall firefox
    rm -rf /tmp/tmp*
    sleep 3
done
