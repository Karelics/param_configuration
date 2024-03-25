FROM ros:humble

# Disable terminal interaction for apt
ENV DEBIAN_FRONTEND=noninteractive

# Make default shell in Dockerfile bash instead of sh
SHELL ["/bin/bash", "-c"]

# Setup workspace and some handy env variables
ENV ROS2_WS=/ros2_ws
RUN mkdir -p ${ROS2_WS}/src
ENV ROS_LOG_DIR=/logs
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp \
    python3-pip \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the necessary files
COPY ./pyproject.toml /
COPY . ${ROS2_WS}/src/param_configuration

# Install pylint for code analysis and install other Python dependencies
RUN pip3 install \
    pylint \
    -r ${ROS2_WS}/src/param_configuration/requirements.txt \
    --no-cache-dir

# Build Parameter Configuration in the newly created workspace
RUN cd ${ROS2_WS} && \
    apt-get update && \
    . /opt/ros/${ROS_DISTRO}/setup.bash && \
    rosdep install --from-paths src --ignore-src -r -y --rosdistro ${ROS_DISTRO} && \
    colcon build --symlink-install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Source ROS and the new workspace automatically when new terminal is opened
RUN echo ". /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc && \
    echo ". ${ROS2_WS}/install/setup.bash" >> ~/.bashrc

# Fix autocompletion
RUN echo 'eval "$(register-python-argcomplete3 colcon)"' >> /opt/ros/${ROS_DISTRO}/setup.sh

# Source the new workspace in the main terminal
COPY docker/param_configuration/ros_entrypoint.sh /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]

CMD ["bash"]
