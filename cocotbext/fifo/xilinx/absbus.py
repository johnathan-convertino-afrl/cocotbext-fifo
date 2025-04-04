#******************************************************************************
# file:    absbus.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/27
#
# about:   Brief
# abstraction of the xilinx fifo bus
#
# license: License MIT
# Copyright 2025 Jay Convertino
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
#******************************************************************************

import cocotb

from cocotbext.busbase import *

import enum

# Class: xilinxFIFOtrans
# create an object that associates a data member and ? for operation.
class xilinxFIFOtrans(transaction):
    def __init__(self, data = None):
        self.data = data

# Class: xilinxFIFOsourceState
# An enum class that provides the current state and will change states per spec.
class xilinxFIFOsourceState(enum.IntEnum):
  IDLE  = 1
  WRITE = 2
  FULL  = 3
  ERROR = 99

# Class: xilinxFIFOsinkState
# An enum class that provides the current state and will change states per spec.
class xilinxFIFOsinkState(enum.IntEnum):
  IDLE  = 1
  READ  = 2
  ERROR = 99

# Class: xilinxFIFObase
# abstract base class that defines Xilinx FIFO signals
class xilinxFIFObase(busbase):
  # Constructor: __init__
  # Setup defaults and call base class constructor.
  def __init__(self, entity, name, clock, resetn, fwft = False, ack = False, *args, **kwargs):

    super().__init__(entity, name, clock, *args, **kwargs)

    self._resetn = resetn

    self._fwft = fwft

    temp = noSignal

    temp.value = not ack

    # Assign a noSignal object with a value attribute. That way if we
    # do a simple if check, acks that don't exist means we do an action anyways.
    self._ack = getattr(self.bus, "ack", temp)
