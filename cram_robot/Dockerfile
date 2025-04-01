FROM ubuntu:20.04
LABEL authors="Clifford Onyonka"

ARG USERNAME=capstone
ARG DEBIAN_FRONTEND=noninteractive

ENV ROS_PYTHON_VERSION=3
ENV ROS_DISTRO=noetic

# Create user, install essential packages, add required apt repositories
RUN apt-get update \
    && apt-get install apt-utils curl build-essential git software-properties-common sudo x11-apps -y \
    && useradd -m ${USERNAME} \
    && passwd -d ${USERNAME} \
    && usermod -aG sudo ${USERNAME} \
    && sudo add-apt-repository universe \
    && sudo add-apt-repository restricted \
    && sudo add-apt-repository multiverse \
    && sudo add-apt-repository ppa:deadsnakes/ppa \
    && sudo sh -c "echo \"deb http://packages.ros.org/ros/ubuntu focal main\" > /etc/apt/sources.list.d/ros-latest.list" \
    && curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add - \
    && sudo apt-get update

USER ${USERNAME}
WORKDIR /home/${USERNAME}

# Install Python3.9, ROS Noetic, and PyCRAM
RUN sudo apt-get update \
    # Python3.9
    && sudo apt-get install python3.9 python3.9-dev python3-apt python3-testresources -y \
    && sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 \
    && sudo update-alternatives --set python3 /usr/bin/python3.9 \
    && curl https://bootstrap.pypa.io/get-pip.py | sudo python3 \
    # ROS Noetic
    && sudo apt-get update \
    && sudo apt-get install ros-noetic-desktop-full -y\
    && echo "export PATH=/opt/ros/noetic/bin:$PATH" >> /home/${USERNAME}/.bashrc\
    && echo "source /opt/ros/noetic/setup.bash" >> /home/${USERNAME}/.bashrc \
    && sudo apt-get install python3-catkin-tools python3-osrf-pycommon python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool -y \
    && pip3 install --upgrade netifaces \
    && sudo rosdep init \
    && rosdep update \
    # PyCRAM
    && sudo apt-get update \
    && sudo apt-get install ros-noetic-pr2-arm-kinematics ros-noetic-pr2-kinematics -y \
    && mkdir -p /home/${USERNAME}/.ssh/ \
    && touch /home/${USERNAME}/.ssh/known_hosts \
    && ssh-keyscan github.com >> /home/${USERNAME}/.ssh/known_hosts \
    && export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no" \
    && /bin/bash -c "source /opt/ros/noetic/setup.bash" \
    && export PATH=/opt/ros/noetic/bin:$PATH \
    && export PYTHONPATH=/opt/ros/noetic/lib/python3/dist-packages:$PYTHONPATH \
    && mkdir -p /home/${USERNAME}/workspace/ros/src \
    && cd /home/${USERNAME}/workspace/ros/src \
    && git config --global url."https://github.com/".insteadOf "git@github.com:" \
    && git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_maps.git \
    && git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_robots.git \
    && git clone --depth 1 --branch dev --single-branch --recursive https://github.com/cram2/pycram.git \
    && git clone --depth 1 --branch master --single-branch --recursive https://github.com/cram2/kdl_ik_service.git \
    && git clone --depth 1 --branch master --single-branch --recursive https://github.com/code-iai/iai_pr2.git \
    && git clone --depth 1 --branch master --single-branch https://github.com/orocos/orocos_kinematics_dynamics.git \
    && rosdep update \
    && rosdep install --ignore-src --from-paths . -r -y \
    && sudo pip3 install --ignore-installed -r pycram/requirements.txt \
    && sudo pip3 install "pybind11[global]==2.13.6"

# PyCRAM port
EXPOSE 11311

CMD ["python3", "-c", "while True: continue"]
