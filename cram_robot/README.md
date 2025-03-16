# CRAM Robot

Run the PR2 robot simulation in a containerised environment

## Usage

1. Install an X Server: one can be found [here](https://sourceforge.net/projects/vcxsrv/), or run `choco install vcxsrv`
if you have Chocolatey
2. Build image: `docker build -t capstone .`
3. Launch the X Server, leaving all settings in their default configuration. However, ensure the following settings are
selected:
    1. `Multiple windows`
    2. `Start no client`
    3. `Disable access control`
4. Set required environment variables: `export DISPLAY=192.168.1.201; export SCREEN=0`. $DISPLAY is the host IP address
and $SCREEN is the screen to use (by default $SCREEN is set to 0 unless the host has multiple screens).
5. Run container: `docker run -d -e DISPLAY=$DISPLAY:$SCREEN --name capstone capstone`. If a container already exists
but is stopped, run `docker start capstone` to restart it.
6. Run CRAM robot:
    1. Exec into container: `docker exec -it capstone bash`
    2. Launch CRAM robot simulator: `roslaunch pycram ik_and_description.launch`
