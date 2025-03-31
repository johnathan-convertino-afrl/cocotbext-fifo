#******************************************************************************
# file:    monitor.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/11
#
# about:   Brief
# Monitor for APB3
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

from ..version import __version__
from .absbus import *

from cocotb.triggers import FallingEdge, RisingEdge, Event
from cocotb.result import TestFailure
from cocotb.binary import BinaryValue
from cocotb.queue import Queue

# Class: apb3Monitor
# Check signals to make sure they are applied properly.
class apb3Monitor(apb3Base):
  # Constructor: __init__
  # Setup defaults and call base class constructor.
  def __init__(self, entity, name, clock, resetn, *args, **kwargs):
    super().__init__(entity, name, clock, resetn, *args, **kwargs)

    self.log.info("APB3 Monitor")
    self.log.info("APB3 Monitor version %s", __version__)
    self.log.info("Copyright (c) 2025 Jay Convertino")
    self.log.info("https://github.com/johnathan-convertino-afrl/cocotbext-apb")

  # Function: _check_type
  # Check and make sure we are only sending apb3trans, this is only here to satisify the need to have it.
  def _check_type(self, trans):
      if(not isinstance(trans, apb3trans)):
          self.log.error(f'Transaction must be of type: {type(apb3trans)}')
          return False

      return True

  # Method: _run
  # _run thread that deals with checking signals, simple check for now.
  async def _run(self):
    self.active = False

    while True:
      await RisingEdge(self.clock)

      # when in reset, check values and idle.
      if not self._resetn.value:
        assert self.bus.psel.value == 0,    "RESET ISSUE: PSEL is not zero."
        assert self.bus.paddr.value == 0,   "RESET ISSUE: PADDR is not zero."
        assert self.bus.penable.value == 0, "RESET ISSUE: PENABLE is not zero."
        assert self.bus.pwrite.value == 0,  "RESET ISSUE: PWRITE is not zero."
        assert self.bus.pwdata.value == 0,  "RESET ISSUE: PWDATA is not zero."
        assert self.bus.prdata.value == 0,  "RESET ISSUE: PRDATA is not zero."
        assert self.bus.pready.value == 0,  "RESET ISSUE: PREADY is not zero."
        self._idle.set()
        continue

      # simple check for now.
      if self.bus.pready.value:
        if not self.bus.psel.value:
          if self.bus.penable.value:
            raise ValueError("PENABLE ISSUE: PENABLE is not zero when PSEL is zero.")


