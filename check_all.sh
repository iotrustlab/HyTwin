#!/bin/bash

echo "
*******************************************************************************
KeYmaera X artifact checking.
*******************************************************************************
"

set -e

while getopts "u:" flag; do
    case $flag in
        u) user=${OPTARG};;
    esac
done

if [ -z "$user" ]
then
  user="$(whoami)"
  if [ -z "$user" ]
  then
    echo "Failed to detect \$user for licenses. Provide username with -u."
    exit 1
  fi
fi

docker start kyx

docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove IV_I_conservative.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove V_I_slopecurve.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove V_II_airbrakes.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove V_II_airbrakes_expanded.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove V_III_taylor.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove VI_I_airbrakes_freight.kyx'
docker exec kyx bash -c 'PATH=$PATH:$(<wepath.txt); java -da -jar keymaerax.jar -launch -prove VI_I_taylor_freight.kyx'

echo "
*******************************************************************************
KeYmaera X all artifacts checked.
*******************************************************************************
"

docker stop kyx
