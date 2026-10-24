"""
Controller node act as controller for Hunter turtle's movement. It takes care of
  * calculate nearest turtle (live turtle list is got from amma node)
  * move towards nearest turtle and eats it
  * this loop over

  * subscribe to topic 'live_turtles' to receive the live turtles data
"""

import math
import rclpy

from rclpy.node import Node

from rosnake_interfaces.msg import TurtleStateArray, TurtleState


class Controller(Node):
  def __init__(self, node_name:str):
    super().__init__(node_name)

    self.hunter = None  # Current State of the Hunter turtle
    self.live = None    # Subscriber constantly updates the variable

    # Subscribtion to 'live_turtles' topic to get the live turtles list
    # The callback lambda function update the self.live variable every time
    # a new message is published in the topic
    self.create_subscription(
      TurtleStateArray,
      'live_turtles',
      lambda msg: setattr(self, 'live', msg.turtles),
      1
    )

    # Subscription to '/turtle'


  @property
  def closest_turtle(self):
    pass









def main(args = None):
  rclpy.init(args = args)

  m = Controller('controller')


  rclpy.spin(m)
  rclpy.shutdown()
