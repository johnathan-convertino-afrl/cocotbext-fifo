#******************************************************************************
# file:    driver.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/27
#
# about:   Brief
# Bus Driver for Xilinx FIFO
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
from cocotb.handle import IntegerObject

# Class: xilinxFIFOsource
# Drive xilinx FIFO write interfaces
class xilinxFIFOsource(xilinxFIFObase):
  # Variable: _signals
  # List of signals that are required
  _signals = ["en", "data", "full"]
  # Variable: _optional_signals
  # List of optional signals, these will never be required but will be used if found.
  _optional_signals = ["ack"]
  # Constructor: __init__
  # Setup defaults and call base class constructor.
  def __init__(self, entity, name, clock, resetn, fwft = False, ack = False, *args, **kwargs):
    super().__init__(entity, name, clock, resetn, fwft, ack, *args, **kwargs)

    self.log.info("Xilinx FIFO Source")
    self.log.info("Xilinx FIFO Source version %s", __version__)
    self.log.info("Copyright (c) 2025 Jay Convertino")
    self.log.info("https://github.com/johnathan-convertino-afrl/cocotbext-fifo")

    self._state = xilinxFIFOsourceState.IDLE

    # setup bus defaults
    self.bus.en.setimmediatevalue(0)
    self.bus.data.setimmediatevalue(0)

  # Function: write
  # Write to a address some data
  async def write(self, data):
    if(isinstance(data, list)):
      temp = []
      for i in data:
        temp.append(xilinxFIFOtrans(i))
      await self.write_trans(temp)
    else:
      await self.write_trans(xilinxFIFOtrans(data))

  # Function: _check_type
  # Check and make sure we are only sending xilinxFIFOtrans
  def _check_type(self, trans):
      if(not isinstance(trans, xilinxFIFOtrans)):
          self.log.error(f'Transaction must be of type: {type(xilinxFIFOtrans)}')
          return False

      return True

  # Method: _run
  # _run thread that deals with read and write queues.
  async def _run(self):
    self.active = False

    trans = None

    while True:
      await RisingEdge(self.clock)

      # when in reset, set values and idle.
      if not self._resetn.value:
        self.bus.en.value   = 0
        self.bus.data.value = 0

        self._idle.set()
        continue

      if(self._state == xilinxFIFOsourceState.IDLE):
        if not self.wqueue.empty() and (self._fwft or not self.bus.full.value):
            self.log.info(f'XILINX FIFO SOURCE STATE: {self._state.name} BUS WRITE')
            trans = await self.wqueue.get()
            self.bus.en.value = 1
            self.bus.data.value = trans.data
            self.active = True
            self._state = xilinxFIFOsourceState.WRITE
            self._idle.set()
      elif(self._state == xilinxFIFOsourceState.WRITE):
        if self.wqueue.empty():
          if self._ack.value:
            self.log.info(f'XILINX FIFO SOURCE STATE: {self._state.name} BUS RELEASE')
            self.bus.en.setimmediatevalue(0)
            self.bus.data.setimmediatevalue(0)
            self.active = False
            self._idle.set()
            self._state = xilinxFIFOsourceState.IDLE
        elif not self.bus.full.value:
          if self._ack.value:
            self.log.info(f'XILINX FIFO SOURCE STATE: {self._state.name} BUS WRITE')
            trans = await self.wqueue.get()
            self.bus.en.value = 1
            self.bus.data.value = trans.data
            self._idle.set()
        else:
          self.log.info(f'XILINX FIFO SOURCE STATE: {self._state.name} BUS FULL')
          self.bus.en.value = 1
          self._state = xilinxFIFOsourceState.FULL
          self._idle.set()
      elif(self._state == xilinxFIFOsourceState.FULL):
        if self._ack.value:
          self.log.info(f'XILINX FIFO SOURCE STATE: {self._state.name} BUS NOT FULL')
          trans = await self.wqueue.get()
          self.bus.en.value = 1
          self.bus.data.value = trans.data
          self._state = xilinxFIFOsourceState.WRITE
          self._idle.set()

# Class: xilinxFIFOsink
# Drive xilinx FIFO read interfaces
class xilinxFIFOsink(xilinxFIFObase):
  # Variable: _signals
  # List of signals that are required
  _signals = ["en", "data", "empty"]
  # Variable: _optional_signals
  # List of optional signals, these will never be required but will be used if found.
  _optional_signals = ["valid"]
  # Constructor: __init__
  # Setup defaults and call base class constructor.
  def __init__(self, entity, name, clock, resetn, fwft = False, *args, **kwargs):
    super().__init__(entity, name, clock, resetn, fwft, *args, **kwargs)

    self.log.info("Xilinx FIFO Sink")
    self.log.info("Xilinx FIFO Sink version %s", __version__)
    self.log.info("Copyright (c) 2025 Jay Convertino")
    self.log.info("https://github.com/johnathan-convertino-afrl/cocotbext-fifo")

    self._state = xilinxFIFOsinkState.IDLE

    # Assign a noSignal object with a value attribute. That way if we
    # do a simple if check, valids that don't exist means we do an action anyways.
    self._valid = getattr(self.bus, "valid", noSignal)

    # setup bus defaults
    self.bus.en.setimmediatevalue(0)


  # Function: write
  # Write to a address some data
  async def write(self, data):
    if(isinstance(data, list)):
      temp = []
      for i in range(len(data)):
        temp.append(data[i])
      await self.write_trans(temp)
    else:
      await self.write_trans(xilinxFIFOtrans(data))

  # Function: read
  # Read from a address and return data
  async def read(self, data):
    trans = None
    if(isinstance(data, list)):
      temp = []
      for d in data:
        temp.append(xilinxFIFOtrans(d))
      temp = await self.read_trans(temp)
      #need a return with the data list only. This is only a guess at this point
      return [temp[i].data for i in range(len(temp))]
    else:
      trans = await self.read_trans(xilinxFIFOtrans(data))
      return trans.data

  # Function: _check_type
  # Check and make sure we are only sending xilinxFIFOtrans
  def _check_type(self, trans):
      if(not isinstance(trans, xilinxFIFOtrans)):
          self.log.error(f'Transaction must be of type: {type(xilinxFIFOtrans)}')
          return False

      return True

  # Method: _run
  # _run thread that deals with read and write queues.
  async def _run(self):
    self.active = False

    trans = None

    while True:
      await RisingEdge(self.clock)

      # when in reset, set values and idle.
      if not self._resetn.value:
        self.bus.en.value   = 0

        self._idle.set()
        continue

      if(self._state == xilinxFIFOsinkState.IDLE):
        if not self.qqueue.empty() and (self._fwft and not self.bus.empty.value):
          self.log.info(f'XILINX FIFO SINK STATE: {self._state.name} BUS READ')
          trans = await self.qqueue.get()
          self.bus.en.value = 1
          if self.bus.valid.value and self._fwft:
            trans.data = self.bus.data.value.integer
            await self.rqueue.put(trans)
          self.active = True
          self._state = xilinxFIFOsinkState.READ
        else:
          self._idle.set()
      elif(self._state == xilinxFIFOsinkState.READ):
        if self.qqueue.empty():
          self.log.info(f'XILINX FIFO SINK STATE: {self._state.name} BUS RELEASE')
          self.bus.en.value = 0
          self.active = False
          self._idle.set()
          self._state = xilinxFIFOsinkState.IDLE
        else:
          if self.bus.valid.value:
            self.log.info(f'XILINX FIFO SINK STATE: {self._state.name} BUS READ')
            trans = await self.qqueue.get()
            self.bus.en.value = 1
            trans.data = self.bus.data.value.integer
            await self.rqueue.put(trans)
            self._idle.set()
