//******************************************************************************
// file:    test.v
//
// author:  JAY CONVERTINO
//
// date:    2025/03/17
//
// about:   Brief
// Test bench for xilinx fifo using cocotb
//
// license: License MIT
// Copyright 2025 Jay Convertino
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to
// deal in the Software without restriction, including without limitation the
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
// sell copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.
//
//******************************************************************************

`timescale 1ns/100ps

/*
 * Module: test
 *
 * Test bench loop for xilinx fifo
 *
 * Parameters:
 *
 *    FIFO_DEPTH    - Depth of the fifo, must be a power of two number(divisable aka 256 = 2^8). Any non-power of two will be rounded up to the next closest.
 *    BYTE_WIDTH    - How many bytes wide the data in/out will be.
 *    FWFT          - 1 for first word fall through mode. 0 for normal.
 *
 * Ports:
 *
 *    rd_clk            - Clock for read data
 *    rd_rstn           - Negative edge reset for read.
 *    rd_en             - Active high enable of read interface.
 *    rd_valid          - Active high output that the data is valid.
 *    rd_data           - Output data
 *    rd_empty          - Active high output when read is empty.
 *    wr_clk            - Clock for write data
 *    wr_rstn           - Negative edge reset for write
 *    wr_en             - Active high enable of write interface.
 *    wr_ack            - Active high when enabled, that data write has been done.
 *    wr_data           - Input data
 *    wr_full           - Active high output that the FIFO is full.
 */
module test #(
    parameter FIFO_DEPTH = 8,
    parameter BYTE_WIDTH = 4,
    parameter FWFT = 1
  )
  (
    input                         rd_clk,
    input                         rd_rstn,
    inout                         rd_en,
    inout                         rd_valid,
    inout   [(BYTE_WIDTH*8)-1:0]  rd_data,
    inout                         rd_empty,
    input                         wr_clk,
    input                         wr_rstn,
    inout                         wr_en,
    inout                         wr_ack,
    inout   [(BYTE_WIDTH*8)-1:0]  wr_data,
    inout                         wr_full
  );

  reg r_wr_en;

  assign rd_data = wr_data;

  assign rd_valid = r_wr_en;

  assign wr_full = 1'b0;

  assign rd_empty = !r_wr_en;

  assign wr_ack = r_wr_en;

  //copy pasta, fst generation
  initial
  begin
    $dumpfile("test.fst");
    $dumpvars(0,test);
  end

  always @(posedge wr_clk)
  begin
    r_wr_en <= wr_en;
  end

endmodule
