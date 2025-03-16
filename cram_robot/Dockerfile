FROM ubuntu:20.04
LABEL authors="Clifford Onyonka"

ARG USERNAME=capstone
ARG DEBIAN_FRONTEND=noninteractive

ENV ROS_PYTHON_VERSION=3
ENV ROS_DISTRO=noetic

# Create user and install essential packages
RUN apt-get update \
    && apt-get install apt-utils curl build-essential git software-properties-common sudo x11-apps -y \
    && useradd -m ${USERNAME} \
    && passwd -d ${USERNAME} \
    && usermod -aG sudo ${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}

# Install Python3.9
COPY ./install_python_3_9.sh ./install_python_3_9.sh
RUN sudo chmod +x ./install_python_3_9.sh \
    && sudo ./install_python_3_9.sh

# Install ROS Noetic
COPY ./install_ros_noetic.sh ./install_ros_noetic.sh
RUN sudo chmod +x ./install_ros_noetic.sh \
    && sudo ./install_ros_noetic.sh \
    && sudo rosdep init \
    && rosdep update

# Install PyCRAM
COPY ./install_pycram.sh ./install_pycram.sh
RUN  sudo chmod +x ./install_pycram.sh \
    && ./install_pycram.sh

# PyCRAM port
EXPOSE 11311

CMD ["python3", "-c", "while True: continue"]
