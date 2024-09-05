"""
Generates a BMP image with horizontal zebra stripes.

The script takes three command line arguments:

    --width: The width of the image in pixels (default: 1080)
    --height: The height of the image in pixels (default: 2376)
    --size: The height of each zebra stripe in pixels (default: 20)

The generated image is saved as a file named "zebra-<width>x<height>-<size>.bmp"
"""

import argparse
import struct

from python_bmp_generator import bmp_header as bh
from python_bmp_generator import bmp_info_header as bih

WHITE = [0xFF, 0xFF, 0xFF]
BLACK = [0x00, 0x00, 0x00]

def create_bitmap(
    width: int, 
    height: int, 
    pattern: list[list[int]], 
    color_depth: int = 24,
    bits_in_byte: int = 8,
    byte_alignment_size: int = 4,
) -> bytearray:
    """
    Creates a BMP image file with the given width, height, and pattern.

    The pattern should be a list of lists of integers, where each sublist
    represents a row in the image. Each integer in the sublist should be
    between 0 and 255, and represents the intensity of the red, green, and
    blue components of the pixel color.

    The color depth of the image is set to 24 bits by default, but can be
    changed with the color_depth parameter.

    The function returns a bytearray containing the contents of the BMP
    file.

    Arguments:
        width (int): The width of the pattern.
        height (int): The height of the pattern.
        pattern (list[list[int]]): The pattern to use for the image.
        color_depth (int, optional): The color depth of the image. Defaults to 24.
        bits_in_byte (int, optional): The number of bits in a byte. Defaults to 8.
        byte_alignment_size (int, optional): The byte alignment size. Defaults to 4.

    Returns:
        bytearray: The contents of the BMP file.

    Raises:
        ValueError: If the height of the pattern is not equal to the height of the image.
        ValueError: If the width of the pattern is not equal to the width of the image.
    """
    file_ba = bytearray()

    byte_per_pixel = (color_depth // bits_in_byte)

    # Validate the size of the pattern
    pattern_height= len(pattern)
    if height != pattern_height:
        raise ValueError(f"The height of the pattern is {pattern_height} but the height of the bitmap is {height}")

    pattern_width = len(pattern[0]) / byte_per_pixel
    if width != pattern_width:
        raise ValueError(f"The width of the pattern is {pattern_width} but the width of the bitmap is {width}")

    # Create File Header Template
    file_ba.extend(bh.HEADER_SIZE * bh.ZERO)

    # Create BITMAPINFOHEADER Template
    file_ba.extend(bih.BMP_INFO_HEADER_SIZE * bh.ZERO)
    
    # hydrate the BITMAPINFOHEADER with the width in pixels
    packed_width = struct.pack('<i', width)
    file_ba[bih.PIXELS_WIDTH_OFFSET:bih.PIXELS_WIDTH_OFFSET + bih.PIXELS_WIDTH_BYTES] = packed_width

    # hydrate the BITMAPINFOHEADER with the height in pixels
    packed_height = struct.pack('<i', height)
    file_ba[bih.PIXELS_HEIGHT_OFFSET:bih.PIXELS_HEIGHT_OFFSET + bih.PIXELS_HEIGHT_BYTES] = packed_height

    # hydrate the ID/Header Field 'BM'.
    file_ba[:bh.HEADER_FIELD_BYTES] = bh.HEADER_FIELD_VALUE

    # hydrate the size of the BITMAPINFOHEADER after it has been hydrated with all other information.
    packed_bih = struct.pack('<i', bih.BMP_INFO_HEADER_SIZE)
    file_ba[bih.HEADER_SIZE_OFFSET:bih.HEADER_SIZE_OFFSET + bih.HEADER_SIZE_BYTES] = packed_bih

    # hydrate the header with the number of color planes (must be 1 according to wikipedia)
    packed_number_of_planes = struct.pack('<h', 1)
    file_ba[bih.NUMBER_OF_COLOR_PLANES_OFFSET:bih.NUMBER_OF_COLOR_PLANES_OFFSET + bih.NUMBER_OF_COLOR_PLANES_BYTES] = packed_number_of_planes

    # hydrate the color bit-depth.
    packed_bit_depth = struct.pack('<h', color_depth)
    file_ba[bih.PIXEL_DEPTH_OFFSET:bih.PIXEL_DEPTH_OFFSET + bih.PIXEL_DEPTH_BYTES] = packed_bit_depth

    # hydrate the header with the offset of the pixel array (after the header data)
    packed_pixels_address = struct.pack('<i', len(file_ba))
    file_ba[bh.PIXEL_ARRAY_STARTING_ADDRESS_OFFSET:bh.PIXEL_ARRAY_STARTING_ADDRESS_OFFSET + bh.PIXEL_ARRAY_STARTING_ADDRESS_BYTES] = packed_pixels_address

    # Create Pixel Array
    pixel_bytes_per_row = (byte_per_pixel * width)
    padding_bytes_per_row = (byte_alignment_size - pixel_bytes_per_row) % byte_alignment_size
    pixel_array = bytearray(pixel for row in pattern for pixel in (row+([0]*padding_bytes_per_row)))
    file_ba.extend(pixel_array)

    # Lastly, hydrate the header with the size of the entire file
    packed_file_size = struct.pack('<i', len(file_ba))
    file_ba[bh.SIZE_OFFSET:bh.SIZE_OFFSET + bh.SIZE_BYTES] = packed_file_size

    return file_ba

def generate_pattern(
    width: int, 
    height: int, 
    size: int
) -> list[list[int]]:
    """
    Generates a pattern of horizontal stripes with the given width, height,
    and size.

    The function returns a list of lists of integers, where each sublist
    represents a row in the image. Each integer in the sublist should be
    between 0 and 255, and represents the intensity of the red, green, and
    blue components of the pixel color.

    Arguments:
        width (int): The width of the pattern.
        height (int): The height of the pattern.
        size (int): The height of each stripe in the pattern.

    Returns:
        list[list[int]]: A list of lists of integers representing the pattern.
    """
    color = WHITE

    pixel_array = []
    for y in range(height):
        row = []

        if y % size == 0:
            color = BLACK if color == WHITE else WHITE

        for x in range(width):
            row.extend(color)

        pixel_array.append(row)

    return pixel_array

def main() -> None:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate a BMP image with horizontal zebra stripes.')
    parser.add_argument('--width', type=int, default=1080, help='Width of the image (default: 1080)')
    parser.add_argument('--height', type=int, default=2376, help='Height of the image (default: 2376)')
    parser.add_argument('--size', type=int, default=20, help='Height of each zebra stripe (default: 20)')
    args = parser.parse_args()

    # Generate the bitmap
    pattern = generate_pattern(args.width, args.height, args.size)
    bitmap = create_bitmap(args.width, args.height, pattern)

    # Save the file
    filename = f"zebra-{args.width}x{args.height}-{args.size}.bmp"
    with open(filename, "wb") as file:
        file.write(bitmap)

if __name__ == '__main__':
    main()
