#!/bin/bash

user_name=capstone

sudo add-apt-repository universe
sudo add-apt-repository restricted
sudo add-apt-repository multiverse

sudo sh -c "echo \"deb http://packages.ros.org/ros/ubuntu focal main\" > /etc/apt/sources.list.d/ros-latest.list"
curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add -

sudo apt-get update
sudo apt-get install ros-noetic-desktop-full -y
echo "export PATH=/opt/ros/noetic/bin:$PATH" >> /home/$user_name/.bashrc
echo "source /opt/ros/noetic/setup.bash" >> /home/$user_name/.bashrc

sudo apt-get install python3-catkin-tools python3-osrf-pycommon python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool -y

pip3 install --upgrade netifaces
