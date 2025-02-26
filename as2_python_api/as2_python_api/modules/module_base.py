"""
module_base.py
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


__authors__ = "Pedro Arias Pérez, Miguel Fernández Cortizas, David Pérez Saura, Rafael Pérez Seguí"
__copyright__ = "Copyright (c) 2022 Universidad Politécnica de Madrid"
__license__ = "BSD-3-Clause"
__version__ = "0.1.0"

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..drone_interface import DroneInterface


class ModuleBase:
    """Module Base
    """
    __alias__ = ""
    __deps__ = []

    def __init__(self, drone: 'DroneInterface', alias: str) -> None:
        # ModuleBase used as mixin to call __init methods from next items at the mro
        try:
            super().__init__(drone)
        except TypeError:
            super().__init__()
        self.__drone = drone
        self.__alias__ = alias
        self.__drone.modules[self.__alias__] = self

    # # Abstrac method
    # def __call__(self, *args: Any, **kwds: Any) -> Any:
    #     raise NotImplementedError

    def __del__(self):
        try:
            # Delete when unloading module
            del self.__drone.modules[self.__alias__]
        except KeyError:
            pass  # Avoid exception when DroneInterface destruction

    # def get_mission_item(self):
    #     return self.__call__.__annotations__

    # def get(self, x, y, z, sped=1.0):
    #     return "{}"
