"""
Controller node act as controller for Hunter turtle's movement. It takes care of
  * calculate nearest turtle (live turtle list is got from amma node)
  * move towards nearest turtle and eats it
  * this loop over

  * subscribe to topic 'live_turtles' to receive the live turtles data
  * subscribe to topic '/turtle1/pose' to get the current state of Hunter turtle

  * publish dead turtle info in topic 'dead_turtle' to notify to remove the dead turtle
"""

import math
import rclpy

from typing import List
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from rosnake_interfaces.msg import TurtleStateArray, TurtleState



class Controller(Node):
  # Collision level determins how close the hunter get to the target
  COLLISION_LEVEL: float = 0.2

  # Proportional gain cofficients (Tune to make the hunter to move faster/slower)
  K_LINEAR = 1.5
  K_ANGULAR = 6

  def __init__(self, node_name:str):
    super().__init__(node_name)

    self.hunter: Pose = Pose()            # Current State of the Hunter turtle
    self.alive: List[TurtleState] = []    # Subscriber constantly updates the variable
    self.dead_turtles = set()

    # Subscribtion to 'alive_turtles' topic to get the live turtles list
    # The callback lambda function update the self.alive variable every time
    # a new message is published in the topic
    self.create_subscription(
      TurtleStateArray,
      'alive_turtles',
      lambda message: setattr(self, 'alive', message.turtles),
      1
    )

    # Subscription to '/turtle/pose' to get current position of Hunter turtle
    self.create_subscription(Pose, '/turtle1/pose', self._pos_subscription_handler, 1)

    # Publisher to publish the dead turtle state to notify to remove it from window
    self.publish_dead = self.create_publisher(TurtleState, 'dead_turtle', 10)

    # Publisher to publish naviagation commands for the Hunter to move
    self.publish_navigation = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)


  def _distance_square(self, origin:Pose, dest:TurtleState) -> float:
    ''' Distance Square: d^2 = (x2 - x1)^2 + (y2 - y1)^2 '''
    return ((dest.x - origin.x)**2 + (dest.y - origin.y)**2)


  @property
  def closest_turtle(self) -> TurtleState:
    ''' Based on Hunter turtle's position, identify the closest turtle '''
    # filter out any turtle that is dead and still in alive list
    available_turtle = [t for t in self.alive if t.name not in self.dead_turtles]

    return min(available_turtle, key=lambda dest: self._distance_square(self.hunter, dest))


  def _pos_subscription_handler(self, message:Pose):
    # on every update of Hunters position, let's call charge for next move
    self.hunter = message

    # check for alive turtles before pursing it
    if not self.alive:
      return

    self.charge()


  def charge(self):
    ''' Run forward quickly in the direction of closest turtle and eat it '''
    # We will move the Hunter towards the target both by moving and turning simultaneously
    target = self.closest_turtle   # TurtleState datatype
    curr_pos = self.hunter         # Pose datatype

    # distance b/w the target turtle and Hunter turtle
    dist_err = math.dist((target.x, target.y), (curr_pos.x, curr_pos.y))

    theta_t = math.atan2(        # target angle to head
      target.y - curr_pos.y,
      target.x - curr_pos.x
    )

    # Calculate the steer angle
    theta_err = theta_t - curr_pos.theta
    # Normalize steer angle error to find the shorted path
    theta_err_sh = math.atan2(math.sin(theta_err), math.cos(theta_err))

    # check for collison
    if dist_err < self.COLLISION_LEVEL:
      # We collided with the target (closest turtle), so publish the target turtle
      # to the Mother node to remove the dead turtle
      self.dead_turtles.add(target.name)

      self.publish_dead.publish(target)
      self.get_logger().info(f'{target.name}: Turtle Dead')
    else:
      # Publish the Navigate command
      twist = Twist()
      twist.linear.x = self.K_LINEAR * dist_err
      twist.angular.z = self.K_ANGULAR * theta_err_sh
      self.publish_navigation.publish(twist)






def main(args = None):
  rclpy.init(args = args)

  m = Controller('controller')

  rclpy.spin(m)
  rclpy.shutdown()
