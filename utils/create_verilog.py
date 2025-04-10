import os
import math

################################################################################
# GENERATE VERILOG VIEW
#
# Generate a .v file based on the given SRAM.
################################################################################

def create_verilog( mem ):

    name  = str(mem.name)
    depth = int(mem.depth)
    bits  = int(mem.width_in_bits)
    num_rwport = int(mem.rw_ports)
    if num_rwport == 1:
      port_suffix = {0: ""}
    else:
      port_suffix = {n: f"_{chr(n+ord('A'))}" for n in range(num_rwport)}
    addr_width = math.ceil(math.log2(depth))

    V_file = open(os.sep.join([mem.results_dir, name + '.v']), 'w')

    V_file.write('module %s\n' % name)
    V_file.write('(\n')
    for i in range(int(num_rwport)) :
      V_file.write('   rd_out%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   addr_in%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   we_in%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   wd_in%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
     V_file.write('   w_mask_in%s,\n' % port_suffix[i])
    V_file.write('   clk,\n')
    V_file.write('   ce_in\n')
    V_file.write(');\n')
    V_file.write('   parameter BITS = %s;\n' % str(bits))
    V_file.write('   parameter WORD_DEPTH = %s;\n' % str(depth))
    V_file.write('   parameter ADDR_WIDTH = %s;\n' % str(addr_width))
    V_file.write('   parameter corrupt_mem_on_X_p = 1;\n')
    V_file.write('\n')
    for i in range(int(num_rwport)) :
      V_file.write('   output reg [BITS-1:0]    rd_out%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input  [ADDR_WIDTH-1:0]  addr_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input                    we_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input  [BITS-1:0]        wd_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
     V_file.write('   input  [BITS-1:0]        w_mask_in%s;\n' % port_suffix[i])
    V_file.write('   input                    clk;\n')
    V_file.write('   input                    ce_in;\n')
    V_file.write('\n')
    V_file.write('   reg    [BITS-1:0]        mem [0:WORD_DEPTH-1];\n')
    V_file.write('\n')
    V_file.write('   integer j;\n')
    V_file.write('\n')
    V_file.write('   always @(posedge clk)\n')
    V_file.write('   begin\n')
    V_file.write('      if (ce_in)\n')
    V_file.write('      begin\n')
    for i in range(int(num_rwport)) :
      V_file.write("         //if ((we_in%s !== 1'b1 && we_in%s !== 1'b0) && corrupt_mem_on_X_p)\n" % (port_suffix[i], port_suffix[i]))
      V_file.write('         if (corrupt_mem_on_X_p &&\n')
      V_file.write("             ((^we_in%s === 1'bx) || (^addr_in%s === 1'bx))\n" % (port_suffix[i], port_suffix[i]))
      V_file.write('            )\n')
      V_file.write('         begin\n')
      V_file.write('            // WEN or ADDR is unknown, so corrupt entire array (using unsynthesizeable for loop)\n')
      V_file.write('            for (j = 0; j < WORD_DEPTH; j = j + 1)\n')
      V_file.write("               mem[j] <= 'x;\n")
      V_file.write(f'            $display("warning: ce_in=1, we_in{port_suffix[i]} is %b, addr_in{port_suffix[i]} = %x in ' + name + '", we_in%s, addr_in%s);\n' % (port_suffix[i], port_suffix[i]))
      V_file.write('         end\n')
      V_file.write('         else if (we_in)\n')
      V_file.write('         begin\n')
      # V_file.write('            mem[addr_in%s] <= (wd_in%s) | (mem[addr_in%s]);\n' % (port_suffix[i], port_suffix[i], port_suffix[i]))
      V_file.write('            mem[addr_in%s] <= (wd_in%s & w_mask_in%s) | (mem[addr_in%s] & ~w_mask_in%s);\n' % (port_suffix[i], port_suffix[i], port_suffix[i], port_suffix[i], port_suffix[i]))
      V_file.write('         end\n')
    V_file.write('         // read\n')
    for i in range(int(num_rwport)) :
      V_file.write('         rd_out%s <= mem[addr_in%s];\n' % (port_suffix[i], port_suffix[i]))
    V_file.write('      end\n')
    V_file.write('      else\n')
    V_file.write('      begin\n')
    V_file.write("         // Make sure read fails if ce_in is low\n")
    for i in range(int(num_rwport)) :
      V_file.write("         rd_out%s <= 'x;\n" % port_suffix[i])
    V_file.write('      end\n')
    V_file.write('   end\n')
    V_file.write('\n')
    V_file.write('   // Timing check placeholders (will be replaced during SDF back-annotation)\n')
    V_file.write('   reg notifier;\n')
    for i in range(int(num_rwport)) :
      V_file.write('   specify\n')
      V_file.write('      // Delay from clk to rd_out\n')
      V_file.write('      (posedge clk *> rd_out%s) = (0, 0);\n' % port_suffix[i])
    V_file.write('\n')
    V_file.write('      // Timing checks\n')
    V_file.write('      $width     (posedge clk,            0, 0, notifier);\n')
    V_file.write('      $width     (negedge clk,            0, 0, notifier);\n')
    V_file.write('      $period    (posedge clk,            0,    notifier);\n')
    for i in range(int(num_rwport)) :
      V_file.write('      $setuphold (posedge clk, we_in%s,     0, 0, notifier);\n' % port_suffix[i])
      V_file.write('      $setuphold (posedge clk, ce_in%s,     0, 0, notifier);\n' % port_suffix[i])
      V_file.write('      $setuphold (posedge clk, addr_in%s,   0, 0, notifier);\n' % port_suffix[i])
      V_file.write('      $setuphold (posedge clk, wd_in%s,     0, 0, notifier);\n' % port_suffix[i])
      V_file.write('      $setuphold (posedge clk, w_mask_in%s, 0, 0, notifier);\n' % port_suffix[i])
    V_file.write('   endspecify\n')
    V_file.write('\n')
    V_file.write('endmodule\n')

    V_file.close()

################################################################################
# GENERATE VERILOG BLACKBOX VIEW
#
# Generate a .bb.v file based on the given SRAM. This is the same as the
# standard verilog view but only has the module definition and port
# declarations (no internal logic).
################################################################################

def generate_verilog_bb( mem ):

    name  = str(mem.name)
    depth = int(mem.depth)
    bits  = int(mem.width_in_bits)
    num_rwport = mem.rw_ports
    addr_width = math.ceil(math.log2(depth))

    num_rwport = int(mem.rw_ports)
    if num_rwport == 1:
      port_suffix = {0: ""}
    else:
      port_suffix = {n: f"_{chr(n+ord('A'))}" for n in range(num_rwport)}
    V_file = open(os.sep.join([mem.results_dir, name + '.bb.v']), 'w')

    V_file.write('module %s\n' % name)
    V_file.write('(\n')
    for i in range(int(num_rwport)) :
      V_file.write('   rd_out%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   addr_in%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   we_in%s,\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   wd_in%s,\n' % port_suffix[i])
    #for i in range(int(num_rwport)) :
    #  V_file.write('   w_mask_in,\n')
    V_file.write('   clk,\n')
    V_file.write('   ce_in\n')
    V_file.write(');\n')
    V_file.write('   parameter BITS = %s;\n' % str(bits))
    V_file.write('   parameter WORD_DEPTH = %s;\n' % str(depth))
    V_file.write('   parameter ADDR_WIDTH = %s;\n' % str(addr_width))
    V_file.write('   parameter corrupt_mem_on_X_p = 1;\n')
    V_file.write('\n')
    for i in range(int(num_rwport)) :
      V_file.write('   output reg [BITS-1:0]    rd_out%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input  [ADDR_WIDTH-1:0]  addr_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input                    we_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
      V_file.write('   input  [BITS-1:0]        wd_in%s;\n' % port_suffix[i])
    for i in range(int(num_rwport)) :
     V_file.write('   input  [BITS-1:0]        w_mask_in%s;\n' % port_suffix[i])
    V_file.write('   input                    clk;\n')
    V_file.write('   input                    ce_in;\n')
    V_file.write('\n')
    V_file.write('endmodule\n')
    V_file.close()
