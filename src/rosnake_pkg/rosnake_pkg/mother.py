"""
Mother node is responsible for creating new turtles and keep track of it. It does
  * create new turtles (act as client)
  * keep track of live turtles
  * kill the turtle that is eaten by snake

  * client to call /spawn service
  * client to call /kill service

  * publish the live turtles at a topic name 'live_turtles'
  * subscription to 'dead_turtle' topic to receive dead turtles
"""

import random
import math
import time
import rclpy

from functools import partial

from rclpy.node import Node

from turtlesim.srv import Spawn, Kill
from rosnake_interfaces.msg import TurtleStateArray, TurtleState



class Mother(Node):
  def __init__(self, node_name:str):
    super().__init__(node_name)

    self.alive = TurtleStateArray()   # keep track of live turtles

    # Client to send request to /spawn server service
    self.spawn_client = self.create_client(Spawn, '/spawn')

    # Client to send reques to /kill server service
    self.kill_client = self.create_client(Kill, '/kill')

    # Create a times to fire this initialization exactly once after 0.5 sec
    self.init_timer = self.create_timer(0.5, self._initialize_turtles)

    # Publisher to publish live turtles data at 10Hz (every 0.1 seconds)
    self.publish_live_turtles = self.create_publisher(TurtleStateArray, 'alive_turtles', 10)
    self.publish_timer = self.create_timer(0.1, lambda: self.publish_live_turtles.publish(self.alive))

    # Subscription to know the dead turtles
    self.create_subscription(TurtleState, 'dead_turtle', self._dead_subscription_handler, 1)


  @property
  def position(self) -> dict:
    '''
    By default, A new turtle is placed at center (x:5, y:5). The dimension of
    window is 10 units in both x and y axis. So any new position should  be b/w
    0 to 10 for both x and y axis. Theta represents the heading direction and
    it's given in radians (range - 0 to 2*PI)
    '''
    return {
      'x': random.uniform(0, 11),
      'y': random.uniform(0, 11),
      'theta': random.uniform(0, math.pi * 2)
    }


  def _initialize_turtles(self):
    # Destroy the timer, so that the initialization won't called again
    self.init_timer.destroy()

    self.get_logger().info("Parturition of initial 5 turtles")
    for _ in range(5):
      self.parturition()

    self.get_logger().info("Initial turtles are born!!!")


  def parturition(self):
    ''' Give birth to a new turtle '''
    # Verify the /spawn server is up and accepting requests
    while not self.spawn_client.wait_for_service(1.0):
      self.get_logger().warn('Service server "/spawn" is not up')

    request = Spawn.Request(**self.position)

    # Make a async request to the server
    future = self.spawn_client.call_async(request)

    # to pass the request object as parmeter, we are using partials
    spawn_req_handler_w_args = partial(self._spawn_request_handler, request)
    future.add_done_callback(spawn_req_handler_w_args)


  def _spawn_request_handler(self, request: Spawn.Request, future):
    # Spawn service server will sent the name of turtle. Add the name along
    # with the position data into the live list
    new_turtle = TurtleState()
    new_turtle.x = request.x
    new_turtle.y = request.y
    new_turtle.name = future.result().name

    self.alive.turtles.append(new_turtle)
    self.get_logger().info(f"New turtle born: {future.result().name}")


  def _dead_subscription_handler(self, dead_turtle:TurtleState):
    '''
    - Remove the dead turtle from the local tracking list.
    - Asynchronously request the /kill service.
    - Wait until the kill completes before spawning a new turtle.
    '''
    # Verify the /kill server is up and accepting requests
    while not self.kill_client.wait_for_service(1.0):
      self.get_logger().warn('Service server "/kill" is not up')

    # Remove the dead turtle from list
    self.alive.turtles = [t for t in self.alive.turtles if t.name != dead_turtle.name]

    # Create & Send Kill request
    request = Kill.Request(name=dead_turtle.name)
    future = self.kill_client.call_async(request)

    # Trigger parturition safely when the Kill command finishes
    future.add_done_callback(lambda fut: self.parturition())








def main(args = None):
  rclpy.init(args = args)

  n = Mother('mother')

  rclpy.spin(n)
  rclpy.shutdown()
