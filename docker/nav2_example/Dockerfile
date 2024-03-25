FROM osrf/ros:humble-desktop-full

# Setup user for Gazebo init mounting and GUI to work correctly
ARG UNAME=user
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} -o ${UNAME}
RUN useradd -m -u ${UID} -g ${GID} -o -s /bin/bash ${UNAME}
RUN usermod -aG sudo ${UNAME}
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER ${UNAME}

# Disable terminal interaction for apt
ENV DEBIAN_FRONTEND=noninteractive

# Make default shell in Dockerfile bash instead of sh
SHELL ["/bin/bash", "-c"]

# Setup workspace and some handy env variables
ENV ROS2_WS=/ros2_ws
RUN sudo mkdir -p ${ROS2_WS}/src && sudo chown -R ${UNAME} ${ROS2_WS}
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Install dependencies
RUN sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-nav2-bringup \
    ros-$ROS_DISTRO-turtlebot3-gazebo \
    python3-pip \
    nano \
    && sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install \
    simpleeval==0.9.13 \
    ruamel.yaml.string==0.1.1 \
    ruamel.yaml==0.18.5 \
    rich==13.7.0 \
    typer==0.9.0 \
    --no-cache-dir

# Build Parameter Configuration in the newly created workspace
COPY . ${ROS2_WS}/src/param_configuration

RUN cd ${ROS2_WS} && \
    sudo apt-get update && \
    . /opt/ros/${ROS_DISTRO}/setup.bash && \
    sudo rosdep install --from-paths src --ignore-src -r -y --rosdistro ${ROS_DISTRO} && \
    colcon build --symlink-install && \
    sudo apt-get clean && \
    sudo rm -rf /var/lib/apt/lists/*

# Source ROS and the new workspace automatically when new terminal is opened
RUN echo ". /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc && \
    echo ". ${ROS2_WS}/install/setup.bash" >> ~/.bashrc

COPY docker/nav2_example/nav2_with_param_configuration.launch.py /nav2_with_param_configuration.launch.py

# Source the new workspace in the main terminal
COPY docker/param_configuration/ros_entrypoint.sh /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

CMD ["bash"]
