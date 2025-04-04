#!/usr/bin/env python
#******************************************************************************
# file:    test.py
#
# author:  JAY CONVERTINO
#
# date:    2025/03/17
#
# about:   Brief
# Cocotb test bench for xilinx fifo
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
# """
#
# Copyright (c) 2020 Alex Forencich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# """

import itertools
import logging
import os
import random

import cocotb_test.simulator

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, NextTimeStep
from cocotb.regression import TestFactory

try:
    from cocotbext.fifo.xilinx import xilinxFIFOsource, xilinxFIFOsink
except ImportError as e:
    import sys
    sys.path.append("../../")
    from cocotbext.fifo.xilinx import xilinxFIFOsource, xilinxFIFOsink

# Class: TB
# Create the device under test which is the master/slave.
class TB:
    def __init__(self, dut):
        self.dut = dut

        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        cocotb.start_soon(Clock(dut.wr_clk, 2, units="ns").start())
        cocotb.start_soon(Clock(dut.rd_clk, 2, units="ns").start())

        self.source  = xilinxFIFOsource(dut, "wr", dut.wr_clk, dut.wr_rstn, dut.FWFT.value != 0)
        self.sink = xilinxFIFOsink(dut, "rd", dut.rd_clk, dut.rd_rstn, dut.FWFT.value != 0)
        # self.monitor = apb3Monitor(dut, "apb", dut.clk, dut.rstn)

    async def reset(self):
        self.dut.wr_rstn.setimmediatevalue(0)
        self.dut.rd_rstn.setimmediatevalue(0)
        await Timer(5, units="ns")
        self.dut.wr_rstn.value = 1
        self.dut.rd_rstn.value = 1

# Function: run_test
# Tests the source/sink for valid transmission of data.
async def run_test(dut, payload_data=None):

    tb = TB(dut)

    await tb.reset()

    # dut.wr_ack.setimmediatevalue(1)

    for test_data in payload_data():

        tb.log.info(f'TEST VALUE : {test_data}')

        await tb.source.write(test_data)

        rx_data = await tb.sink.read(test_data)

        # assert test_data == rx_data, "RECEIVED DATA DOES NOT MATCH"

# Function: incrementing_payload
# Generate a list of ints that increment from 0 to 2^8
def incrementing_payload():
    return list(range(2**8))

# # Function: random_payload
# # Generate a list of random ints 2^16 in the range of 0 to 2^16
# def random_payload():
#     return random.sample(range(2**16), 2**16)


# If its a sim... create the test factory with these options.
if cocotb.SIM_NAME:

    factory = TestFactory(run_test)
    factory.add_option("payload_data", [incrementing_payload])
    factory.generate_tests()


# cocotb-test
tests_dir = os.path.dirname(__file__)

# Function: test
# Main cocotb function that specifies how to put the test together.
def test(request):
    dut = "test"
    module = os.path.splitext(os.path.basename(__file__))[0]
    toplevel = dut

    verilog_sources = [
        os.path.join(tests_dir, f"{dut}.v"),
    ]

    parameters = {}

    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    sim_build = os.path.join(tests_dir, "sim_build",
        request.node.name.replace('[', '-').replace(']', ''))

    cocotb_test.simulator.run(
        python_search=[tests_dir],
        verilog_sources=verilog_sources,
        toplevel=toplevel,
        module=module,
        parameters=parameters,
        sim_build=sim_build,
        extra_env=extra_env,
    )
