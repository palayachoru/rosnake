To run this
```
# Generate build files under install
colcon build

# Source the files, so that ROS2 know about the packages
source install/local_setup.bash

# Using launch file, launch 3 nodes
ros2 launch rosnake_bringup rosnake.launch.xml

Now you will see the turtle eating turtles, like snake game
```
