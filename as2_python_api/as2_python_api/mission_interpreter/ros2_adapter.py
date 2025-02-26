"""
ros2_adapter.py
"""

# Copyright 2022 Universidad Politécnica de Madrid
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


__authors__ = "Pedro Arias Pérez"
__copyright__ = "Copyright (c) 2022 Universidad Politécnica de Madrid"
__license__ = "BSD-3-Clause"

import argparse
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_system_default
import rclpy.executors
from std_msgs.msg import String
from as2_msgs.msg import MissionUpdate
from as2_python_api.mission_interpreter.mission import Mission
from as2_python_api.mission_interpreter.mission_interpreter import MissionInterpreter


class Adapter(Node):
    """ROS 2 Adapter to mission interpreter"""

    STATUS_FREQ = 0.5

    def __init__(self, drone_id: str, use_sim_time: bool = False):
        super().__init__('adapter', namespace=drone_id)

        self.param_use_sim_time = Parameter(
            'use_sim_time', Parameter.Type.BOOL, use_sim_time)
        self.set_parameters([self.param_use_sim_time])

        # self.namespace = drone_id
        self.namespace = 0
        self.interpreter = MissionInterpreter(use_sim_time=use_sim_time)
        self.abort_mission = None

        self.mission_update_sub = self.create_subscription(
            MissionUpdate, '/mission_update', self.mission_update_callback,
            qos_profile_system_default)

        self.mission_status_pub = self.create_publisher(
            String, '/mission_status', qos_profile_system_default)

        self.mission_state_timer = self.create_timer(
            1/self.STATUS_FREQ, self.status_timer_callback)

        self.get_logger().info("Adapter ready")

    def status_timer_callback(self):
        """Publish new mission status"""
        msg = String()
        msg.data = self.interpreter.status.json()
        self.mission_status_pub.publish(msg)

    def mission_update_callback(self, msg: MissionUpdate):
        """New mission update"""
        if msg.drone_id != self.namespace:
            return

        if msg.type == MissionUpdate.EXECUTE:
            self.execute_callback(Mission.parse_raw(msg.mission))
        elif msg.type == MissionUpdate.LOAD:
            if msg.mission_id == 33:
                self.abort_mission = Mission.parse_raw(msg.mission)
                self.get_logger().info("Mission Abort loaded.")
                return
            self.get_logger().info(f"Mission {msg.mission_id} loaded.")
            self.interpreter.reset(Mission.parse_raw(msg.mission))
        elif msg.type == MissionUpdate.START:
            self.start_callback()
        elif msg.type == MissionUpdate.PAUSE:
            self.interpreter.pause_mission()
        elif msg.type == MissionUpdate.RESUME:
            self.interpreter.resume_mission()
        elif msg.type == MissionUpdate.STOP:
            self.interpreter.next_item()
        elif msg.type == MissionUpdate.ABORT:
            self.abort_callback()

    def execute_callback(self, mission: Mission):
        """Load and start mission"""
        self.interpreter.reset(mission)
        self.start_callback()

    def start_callback(self):
        """Start mission on interpreter"""
        try:
            self.interpreter.drone.arm()
            self.interpreter.drone.offboard()
            self.interpreter.start_mission()
        except AttributeError:
            self.get_logger().error("Trying to start mission but no mission is loaded.")

    # TODO: WARNING! This is temporary, move abort mission to MissionInterpreter
    def abort_callback(self):
        """Abort mission on interpreter"""
        if self.abort_mission is None:
            self.get_logger().fatal(
                "Abort command received but not abort mission available. Change to manual control!")
            return

        self.interpreter.reset(self.abort_mission)
        try:
            self.interpreter.start_mission()
        except AttributeError:
            self.get_logger().error("Trying to start mission but no mission is loaded.")


def main():
    """Run node"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=str, default='drone0',
                        help='Namespace')
    parser.add_argument(
        '--use_sim_time', action='store_true', help='Use sim time')

    argument_parser = parser.parse_args()

    rclpy.init()
    print(f"{argument_parser.use_sim_time=}")

    adapter = Adapter(
        drone_id=argument_parser.n, use_sim_time=argument_parser.use_sim_time)

    rclpy.spin(adapter)

    adapter.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
