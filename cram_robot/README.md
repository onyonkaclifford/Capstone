# CRAM Robot

Run the PR2 robot simulation in a containerised environment

## Usage

1. Install an X Server: one can be found [here](https://sourceforge.net/projects/vcxsrv/), or run `choco install vcxsrv`
if you have Chocolatey
2. Build image: `docker build -t cram_robot .`
3. Launch the X Server, leaving all settings in their default configuration. However, ensure the following settings are
selected:
    1. `Multiple windows`
    2. `Start no client`
    3. `Disable access control`
4. Set required environment variables: `export DISPLAY=192.168.1.201; export SCREEN=0`. $DISPLAY is the host IP address
and $SCREEN is the screen to use (by default $SCREEN is set to 0 unless the host has multiple screens).
5. Run container: `docker run -d -e DISPLAY=$DISPLAY:$SCREEN -v </path/to/RoboCRAM/dir>:/home/capstone/src --name cram_robot cram_robot`.
If a container already exists but is stopped, run `docker start cram_robot` to restart it instead of running a new
container.
6. Run CRAM robot (take note of the IMPORTANT section below before proceeding with this step):
    1. Exec into container: `docker exec -it cram_robot bash`
    2. Launch PyCRAM in the background: `roslaunch pycram ik_and_description.launch &`

> [!IMPORTANT]
> On the first run of a new docker container, follow the steps below before running PyCRAM:

1. Exec into container: `docker exec -it cram_robot bash`
2. Navigate to workspace: `cd /home/capstone/workspace/ros`
3. Build workspace: `catkin build`
4. Source required script: `source /home/capstone/workspace/ros/devel/setup.bash`
5. Set automatic sourcing of required script: `echo "source /home/capstone/workspace/ros/devel/setup.bash" >> /home/capstone/.bashrc`
