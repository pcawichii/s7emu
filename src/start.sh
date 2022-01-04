#!/usr/bin/env bash

nohup python ver.py &

sleep 1

python seed.py

python api.py

# python ver.py
