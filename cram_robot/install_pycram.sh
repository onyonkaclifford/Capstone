#!/bin/bash

user_name=capstone

sudo apt-get update
sudo apt-get install ros-noetic-pr2-arm-kinematics ros-noetic-pr2-kinematics -y

mkdir -p /home/$user_name/.ssh/
touch /home/$user_name/.ssh/known_hosts
ssh-keyscan github.com >> /home/$user_name/.ssh/known_hosts

export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no"
mkdir -p /home/$user_name/workspace/ros/src
cd /home/$user_name/workspace/ros/src
git config --global url."https://github.com/".insteadOf "git@github.com:"
git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_maps.git
git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_robots.git
git clone --depth 1 --branch dev --single-branch --recursive https://github.com/cram2/pycram.git
git clone --depth 1 --branch master --single-branch --recursive https://github.com/cram2/kdl_ik_service.git
git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_pr2.git
git clone --depth 1 --branch master --single-branch https://github.com/orocos/orocos_kinematics_dynamics.git

# rosdep update
# rosdep install --ignore-src --from-paths . -r -y

# sudo pip3 install --ignore-installed -r pycram/requirements.txt
# sudo pip3 install "pybind11[global]==2.13.6"
#### sudo pip3 install --force-reinstall matplotlib
#### sudo pip3 install numpy==1.26.0

#### source /home/$user_name/.bashrc
# cd /home/$user_name/workspace/ros && catkin build
# echo "source /home/$user_name/workspace/ros/devel/setup.bash" >> /home/$user_name/.bashrc

#### mkdir -p /home/$user_name/.ipython/profile_default/startup/
#### cp /home/$user_name/workspace/ros/src/pycram/script/ipython_helper/* /home/$user_name/.ipython/profile_default/startup/
