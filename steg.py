import sys
import os
from PIL import Image



def file_to_bits(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return ''.join(format(byte, "08b") for byte in data)

def bits_to_file(bits, output_file):
    bytes_data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            bytes_data.append(int(byte, 2))
    with open(output_file, "wb") as f:
        f.write(bytes_data)

def encode(input_image_path, output_image_path, file_path):
    img = Image.open(input_image_path).convert("RGBA")
    encoded = img.copy()
    width, height = img.size
    index = 0
    
    filename = os.path.basename(file_path)
    filename_bits = ''.join(format(byte, "08b") for byte in filename.encode('utf-8'))
    filename_len_bits = format(len(filename.encode('utf-8')), '08b')

    file_bits = file_to_bits(file_path)
    data_len_bits = format(len(file_bits), '064b')

    binary_data = filename_len_bits + filename_bits + data_len_bits + file_bits

    for row in range(height):
        for col in range(width):
            if index < len(binary_data):
                pixel = list(img.getpixel((col, row)))
                
                if index < len(binary_data):
                    pixel[0] = (pixel[0] & ~1) | int(binary_data[index])
                    index += 1
                if index < len(binary_data):
                    pixel[1] = (pixel[1] & ~1) | int(binary_data[index])
                    index += 1
                if index < len(binary_data):
                    pixel[2] = (pixel[2] & ~1) | int(binary_data[index])
                    index += 1
                
                encoded.putpixel((col, row), tuple(pixel))
            else:
                break
    
    encoded.save(output_image_path)
    print(f"File {file_path} encoded into {output_image_path}")

def decode(image_path, output_file=None):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    bits = []
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))
            bits.append(str(pixel[0] & 1))
            bits.append(str(pixel[1] & 1))
            bits.append(str(pixel[2] & 1))

    if len(bits) < 8:
        print("Cannot read filename length.")
        return

    # Read filename length (8 bits)
    filename_len = int("".join(bits[:8]), 2)
    
    # Read filename
    filename_end_offset = 8 + filename_len * 8
    if len(bits) < filename_end_offset:
        print("Cannot read filename.")
        return
    filename_bits = "".join(bits[8:filename_end_offset])
    filename_bytes = bytearray(int(filename_bits[i:i+8], 2) for i in range(0, len(filename_bits), 8))
    filename = filename_bytes.decode('utf-8')

    # Read data length (64 bits)
    data_len_start_offset = filename_end_offset
    data_len_end_offset = data_len_start_offset + 64
    if len(bits) < data_len_end_offset:
        print("Cannot read data length.")
        return
    data_len = int("".join(bits[data_len_start_offset:data_len_end_offset]), 2)

    # Read data
    data_start_offset = data_len_end_offset
    data_end_offset = data_start_offset + data_len
    if len(bits) < data_end_offset:
        print("Cannot read all data. File may be corrupt.")
        return
    
    binary_data = "".join(bits[data_start_offset:data_end_offset])

    if output_file is None:
        output_file = filename

    bits_to_file(binary_data, output_file)
    print(f"Decoded file written to {output_file}")

def list_hidden_files(image_path):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    bits = []
    max_pixels_to_read = 1024 # A safe number of pixels to read to get the metadata
    pixels_read = 0

    for row in range(height):
        for col in range(width):
            if pixels_read >= max_pixels_to_read:
                break
            pixel = img.getpixel((col, row))
            bits.append(str(pixel[0] & 1))
            bits.append(str(pixel[1] & 1))
            bits.append(str(pixel[2] & 1))
            pixels_read += 1
        if pixels_read >= max_pixels_to_read:
            break

    if len(bits) < 8:
        print("Cannot read filename length.")
        return

    # Read filename length (8 bits)
    filename_len = int("".join(bits[:8]), 2)
    
    # Read filename
    filename_end_offset = 8 + filename_len * 8
    if len(bits) < filename_end_offset:
        print("Cannot read filename.")
        return
    filename_bits = "".join(bits[8:filename_end_offset])
    filename_bytes = bytearray(int(filename_bits[i:i+8], 2) for i in range(0, len(filename_bits), 8))
    filename = filename_bytes.decode('utf-8')

    # Read data length (64 bits)
    data_len_start_offset = filename_end_offset
    data_len_end_offset = data_len_start_offset + 64
    if len(bits) < data_len_end_offset:
        print("Cannot read data length.")
        return
    data_len_in_bits = int("".join(bits[data_len_start_offset:data_len_end_offset]), 2)
    data_len_in_bytes = data_len_in_bits // 8

    print(f"Hidden file: {filename}")
    print(f"Size: {data_len_in_bytes} bytes")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Encode: python steg.py e input.png output.png file_to_hide")
        print("  Decode: python steg.py d encoded.png [output_file]")
        print("  List:   python steg.py l encoded.png")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'e':
        if len(sys.argv) != 5:
            print("Usage: python steg.py e input.png output.png file_to_hide")
            sys.exit(1)
        _, _, input_img, output_img, file_path = sys.argv
        encode(input_img, output_img, file_path)

    elif mode == 'd':
        if len(sys.argv) not in [3, 4]:
            print("Usage: python steg.py d encoded.png [output_file]")
            sys.exit(1)
        
        encoded_img = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) == 4 else None
        decode(encoded_img, output_file)

    elif mode == 'l':
        if len(sys.argv) != 3:
            print("Usage: python steg.py l encoded.png")
            sys.exit(1)
        _, _, encoded_img = sys.argv
        list_hidden_files(encoded_img)

    else:
        print("Invalid mode. Use 'e' for encode, 'd' for decode, or 'l' for list.")
        sys.exit(1)