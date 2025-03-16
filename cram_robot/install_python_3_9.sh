#!/bin/bash

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update

sudo apt-get install python3.9 python3.9-dev python3-testresources -y

sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
sudo update-alternatives --set python3 /usr/bin/python3.9

curl https://bootstrap.pypa.io/get-pip.py | sudo python3
