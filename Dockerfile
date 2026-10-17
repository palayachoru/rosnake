# Use the official OSRF ROS 2 Jazzy Desktop image
FROM osrf/ros:jazzy-desktop-full

# Update and install essential development tools (finally delete cache files)
RUN apt update && apt install -y \
    ros-dev-tools \
    python3-colcon-common-extensions \
    python3-pip \
    git \
    tmux \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Grant 'ubuntu' user with passwordless sudo
RUN echo "ubuntu ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/ubuntu \
    chmod 0440 /etc/sudoers.d/ubuntu

# Automatically source Jazzy Jalisco in every new terminal (for ubuntu user)
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/ubuntu/.bashrc

# Update the terminal prompt like redhat
RUN printf "export PS1='\[\e[0;32m\][\[\e[1;32m\]\u@\h\[\e[0m\] \[\e[1;34m\]\W\[\e[0;32m\]]\[\e[1;36m\]\\\\$ \[\e[0m\]'\n" >> /home/ubuntu/.bashrc


# Set default work directory
WORKDIR /workspaces/rosnake

# Default command to run on start of container
CMD ["bash"]
