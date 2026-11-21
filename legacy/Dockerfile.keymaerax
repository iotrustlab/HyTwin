ARG MATLAB_VERSION=r2021b

FROM mathworks/matlab-deps:${MATLAB_VERSION}

ARG SCALA_VERSION=2.12.8
ARG SBT_VERSION=1.3.7
ARG WOLFRAM_ENGINE_PATH=/usr/local/Wolfram/WolframEngine
ARG DEBIAN_FRONTEND=noninteractive
ARG USER_NAME
ENV TZ=America/New_York

# Add user and grant sudo permission.
RUN adduser --shell /bin/bash --disabled-password --gecos "" ${USER_NAME} && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/${USER_NAME} && \
    chmod 0440 /etc/sudoers.d/${USER_NAME}

# repeat MATLAB_VERSION, otherwise it's not available in Matlab install
ARG MATLAB_VERSION

# Install requirements
RUN apt-get --yes update && \
  apt-get --yes upgrade && \
  apt-get --no-install-recommends --yes install \
    apt-utils \
    software-properties-common \
    curl \
    avahi-daemon \
    wget \
    unzip \
    zip \
    build-essential \
    openjdk-8-jre-headless \
    openjdk-8-jdk \
    git \
    sshpass \
    sudo \
    locales \
    locales-all \
    ssh \
    vim \
    expect \
    libfontconfig1 \
    libgl1-mesa-glx \
    libasound2 \
    util-linux \
    ca-certificates && \
  apt-get clean && \
  apt-get autoremove && \
  rm -rf /var/lib/apt/lists/*

USER ${USER_NAME}
WORKDIR /home/${USER_NAME}

RUN sudo systemctl enable avahi-daemon

# Install Scala
WORKDIR /tmp/
RUN wget -P /tmp https://www.scala-lang.org/files/archive/scala-${SCALA_VERSION}.deb && \
  sudo dpkg -i scala-${SCALA_VERSION}.deb && \
  sudo apt-get --yes update && \
  sudo apt-get --yes upgrade && \
  sudo apt-get --yes install scala && \
  sudo apt-get clean && \
  sudo apt-get autoremove && \
  rm scala-${SCALA_VERSION}.deb

# Install SBT
RUN wget https://scala.jfrog.io/artifactory/debian/sbt-${SBT_VERSION}.deb && \
  sudo dpkg -i sbt-${SBT_VERSION}.deb && \
  sudo apt-get --yes update && \
  sudo apt-get --yes upgrade && \
  sudo apt-get --yes install sbt && \
  rm sbt-${SBT_VERSION}.deb

# Install Wolfram Engine
RUN sudo bash -c 'echo "en_US.UTF-8 UTF-8" > /etc/locale.gen' && \
  sudo locale-gen
RUN wget https://account.wolfram.com/download/public/wolfram-engine/desktop/LINUX && \
  sudo bash LINUX -- -auto -verbose && \
  rm LINUX

# Pull KeYmaera X
WORKDIR /home/${USER_NAME}/
# avoid caching git clone by adding the latest commit SHA to the container
ADD https://api.github.com/repos/LS-Lab/KeYmaeraX-release/git/refs/heads/master kyx-version.json
RUN git clone -n https://github.com/LS-Lab/KeYmaeraX-release.git
ADD https://api.github.com/repos/LS-Lab/KeYmaeraX-projects/git/refs/heads/master projects-version.json
WORKDIR /home/${USER_NAME}/KeYmaeraX-release/keymaerax-webui/src/main/resources/
RUN git clone --depth 1 https://github.com/LS-Lab/KeYmaeraX-projects.git

# Build KeYmaera X at commit
WORKDIR /home/${USER_NAME}/KeYmaeraX-release/
RUN git checkout 22aa7869bc5039e7ecbf7d842fb48e4a01c4cd3d
RUN ls ${WOLFRAM_ENGINE_PATH} > weversion.txt
RUN bash -l -c "echo \"mathematica.jlink.path=${WOLFRAM_ENGINE_PATH}/"'$(<weversion.txt)/SystemFiles/Links/JLink/JLink.jar" > local.properties'
ENV SBT_OPTS="-XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled -Xmx4G"
RUN sbt clean assembly
RUN cp keymaerax-webui/target/scala-2.12/KeYmaeraX*.jar /home/${USER_NAME}/keymaerax.jar

# Export Wolfram Engine version for setup.sh and path for check_all.sh
WORKDIR /home/${USER_NAME}/
RUN ls ${WOLFRAM_ENGINE_PATH} > weversion.txt
RUN bash -l -c "echo \"${WOLFRAM_ENGINE_PATH}/"'$(<weversion.txt)/Executables" > wepath.txt'

# Import artifacts
WORKDIR /home/${USER_NAME}
ADD *.kyx ./

# Create symlink to WolframEngine math (needed by Mathlink make file)
RUN bash -l -c "sudo ln -s "'$(<wepath.txt)/math /usr/local/bin/math'

# Set final working directory
WORKDIR /home/${USER_NAME}/
