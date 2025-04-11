import math


def get_macro_dimensions(process, sram_data):
    column_mux_factor = process.column_mux_factor
    width_in_bits = int(sram_data["width"])
    depth = int(sram_data["depth"])
    num_banks = int(sram_data["banks"])

    bitcell_height = process.bitcell_height_nm / 1000.0
    bitcell_width = process.bitcell_width_nm / 1000.0

    all_bitcell_height = bitcell_height * depth
    all_bitcell_width = bitcell_width * width_in_bits

    if num_banks == 2 or num_banks == 4:
        all_bitcell_height = all_bitcell_height / num_banks
        all_bitcell_width = all_bitcell_width * num_banks
    elif num_banks != 1:
        raise Exception("Unsupported number of banks: {}".format(num_banks))

    all_bitcell_height = all_bitcell_height / column_mux_factor
    all_bitcell_width = all_bitcell_width * column_mux_factor

    total_height = all_bitcell_height * 1.2
    total_width = all_bitcell_width * 1.2 * math.sqrt(float(sram_data["rw_ports"]))

    return total_height, total_width
