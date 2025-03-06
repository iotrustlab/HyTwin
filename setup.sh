#!/bin/bash

# The script can be invoked with -u, -l, and -m options

# -u USERNAME specifies the username to be used in the Docker image
# If not specified, the script will try to use your current username

# -m MAC_ADDRESS specifies the MAC address
# If not specified, the script will try to guess a default address

# run example
# setup.sh -m MAC_ADDRESS

set -e

while getopts "l:m:u:" flag; do
    case $flag in
        m) macaddr=${OPTARG};;
        u) user=${OPTARG};;
    esac
done

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    # *)          machine="UNKNOWN:${unameOut}"
esac
echo "Running on $machine"
case "$machine" in
  Linux)  ethif=eth0;;
  Mac)    ethif=en0;;
esac


if [ -z "$user" ]
then
  user="$(whoami)"
  if [ -z "$user" ]
  then
    echo "Failed to detect \$user for setup. Provide username with -u."
    exit 1
  fi
fi

if [ -z "$macaddr" ]
then
  macaddr="$(ifconfig $ethif | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}')"
  if [ -z "$macaddr" ]
  then
    echo "Failed to detect \$macaddr for setup. Provide MAC address with -m."
    exit 1
  fi
fi

# Set up licensing for WolframEngine
# The folder for Licensing is given lax permissions so that WolframEngine's activation process inside Docker can write to it
mkdir -p Licensing
chmod -R 757 "$PWD/Licensing"

docker rm -f kyx
docker build --build-arg LICENSE_FILE=matlab.lic --build-arg USER_NAME=$user -t keymaerax .
docker create --mac-address $macaddr -it -v $PWD/Licensing:/home/$user/.WolframEngine/Licensing -w /home/$user/ -p 8090:8090 --name kyx keymaerax bash
docker start kyx

# activate Wolfram Engine, comment out or abort this step with Ctrl-d to re-initialize the container
# if Wolfram Engine was activated earlier already
echo ""
echo "If you want to re-initialize the container but keep an earlier Wolfram Engine license: abort Wolfram Engine activation with Ctrl-d and comment out line 71 of setup.sh"
echo ""
docker exec -it kyx wolframscript "-activate"

# initialize .keymaerax directory with Z3
docker exec -it kyx bash -c 'java -da -jar keymaerax.jar -launch -setup'

# add and modify configuration
docker cp ./keymaerax.math.conf kyx:/home/$user/keymaerax.conf
docker exec -it kyx bash -c 'rm .keymaerax/keymaerax.conf;cp keymaerax.conf .keymaerax/keymaerax.conf'
docker exec -it kyx bash -c 'echo "WOLFRAMENGINE_LINK_NAME = /usr/local/Wolfram/WolframEngine/$(<weversion.txt)/Executables/MathKernel" >> .keymaerax/keymaerax.conf'
docker exec -it kyx bash -c 'echo "WOLFRAMENGINE_JLINK_LIB_DIR = /usr/local/Wolfram/WolframEngine/$(<weversion.txt)/SystemFiles/Links/JLink/SystemFiles/Libraries/Linux-x86-64" >> .keymaerax/keymaerax.conf'
docker exec -it kyx bash -c 'echo "WOLFRAMENGINE_TCPIP = false" >> .keymaerax/keymaerax.conf'
docker exec -it kyx bash -c 'echo "IS_DOCKER = true" >> .keymaerax/keymaerax.conf'
docker exec -it kyx sed -i "s/QE_TOOL = z3/QE_TOOL = wolframengine/g" .keymaerax/keymaerax.conf
docker inspect -f '{{ .NetworkSettings.IPAddress }}' kyx > dockerip.txt
docker exec -it kyx sed -i "s/HOST = 127.0.0.1/HOST = $(<dockerip.txt)/g" .keymaerax/keymaerax.conf

# store the changes before exiting
docker commit kyx

docker stop kyx
