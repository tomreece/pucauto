#!/bin/bash

while true; do
    python pucauto.py
    echo Restarting...
    killall firefox
    sleep 3
done
