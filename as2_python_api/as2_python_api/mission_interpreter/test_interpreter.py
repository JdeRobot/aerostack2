"""
test_interpreter.py
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
__version__ = "0.1.0"

import unittest

import rclpy

from as2_python_api.mission_interpreter.mission import Mission
from as2_python_api.mission_interpreter.mission_interpreter import MissionInterpreter


class TestMission(unittest.TestCase):
    """Mission testing"""

    def test_dummy(self):
        """a doctest in a docstring

        >>> test_dummy()
        test called with arg1=1.0, arg2=2.0 and wait=False
        test called with arg1=99.0, arg2=99.0 and wait=False
        """

        mission = Mission.parse_file("dummy_mission.json")

        interpreter = MissionInterpreter(mission)
        interpreter.perform_mission()
        interpreter.shutdown()

    def test_mission_model(self):
        """Test mission stack"""
        dummy_mission = """
        {
            "target": "drone_0",
            "verbose": "True",
            "plan": [
                {
                    "behavior": "test",
                    "args": {
                        "arg1": 1.0,
                        "arg2": 2.0,
                        "wait": "False"
                    }
                },
                {
                    "behavior": "test",
                    "args": {
                        "arg2": 98.0,
                        "arg1": 99.0,
                        "wait": "False"
                    }
                }
            ]
        }"""
        mission = Mission.parse_raw(dummy_mission)
        stack = mission.stack
        item = stack.next()
        assert item == ('test', [1.0, 2.0, 'False'])

        item = stack.next()
        assert item == ('test', [99.0, 98.0, 'False'])

    def test_load_modules(self):
        """Test if modules are loaded correctly
        """

        mission = Mission.parse_file("my_mission.json")

        interpreter = MissionInterpreter(mission)
        assert sorted(interpreter.drone.modules.keys()) == [
            "go_to", "land", "takeoff"
        ]

        assert list(item[0] for item in interpreter.mission_stack.pending) == [
            "takeoff", "go_to", "go_to", "land"
        ]
        interpreter.shutdown()

    # def test(self):
    #     import doctest
    #     doctest.testmod()


if __name__ == "__main__":
    rclpy.init()

    unittest.main()
    rclpy.shutdown()
