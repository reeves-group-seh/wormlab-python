"""
Backends abstract program interaction with non-UI components (hardware). Every
backend provides an ABC which defines the resource's public interface and a
number of concrete implementations in their respective modules.

- `ArduinoBackend`: handles serial communication with the stage-control Arduino.
- `CameraBackend`: handles the reading of frames from the connected stage
  camera.
- `DataBackend`: handles the writing of data to disk.
"""

# relative
from . import arduino, camera, data
from .arduino import ArduinoBackend
from .camera import CameraBackend
from .data import DataBackend

# public api
__all__ = [
    # modules
    "arduino",
    "camera",
    "data",
    # abc
    "ArduinoBackend",
    "CameraBackend",
    "DataBackend",
]
