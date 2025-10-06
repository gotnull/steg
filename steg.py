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

def encode(input_image_path, output_image_path, file_paths):
    img = Image.open(input_image_path).convert("RGBA")
    encoded = img.copy()
    width, height = img.size
    index = 0

    MAGIC_NUMBER = "0101010101010101" # 16 bits

    num_files = len(file_paths)
    if num_files > 255: # 8 bits for num_files
        print("Error: Cannot hide more than 255 files.")
        sys.exit(1)
    num_files_bits = format(num_files, '08b')

    binary_data = MAGIC_NUMBER + num_files_bits # Prepend magic number
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        filename_bytes = filename.encode('utf-8')
        filename_bits = ''.join(format(byte, "08b") for byte in filename_bytes)
        filename_len_bits = format(len(filename_bytes), '08b')

        file_bits = file_to_bits(file_path)
        data_len_bits = format(len(file_bits), '064b')

        binary_data += filename_len_bits + filename_bits + data_len_bits + file_bits

    # Capacity check
    image_capacity_bits = width * height * 3
    if len(binary_data) > image_capacity_bits:
        print(f"Error: Not enough capacity in the image to hide all data.")
        print(f"Required bits: {len(binary_data)}, Image capacity: {image_capacity_bits}")
        sys.exit(1)

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
    print(f"Files {', '.join(file_paths)} encoded into {output_image_path}")

def decode(image_path, output_dir="."):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    bits = []
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))
            bits.append(str(pixel[0] & 1))
            bits.append(str(pixel[1] & 1))
            bits.append(str(pixel[2] & 1))

    MAGIC_NUMBER = "0101010101010101" # 16 bits
    MAGIC_NUMBER_LEN = len(MAGIC_NUMBER)

    current_offset = 0

    # Read magic number
    if len(bits) < current_offset + MAGIC_NUMBER_LEN:
        print("No hidden files found in the image (not enough bits for magic number).")
        return
    
    read_magic_number = "".join(bits[current_offset : current_offset + MAGIC_NUMBER_LEN])
    current_offset += MAGIC_NUMBER_LEN

    if read_magic_number != MAGIC_NUMBER:
        print("No hidden files found in the image (magic number mismatch).")
        return

    # Read number of files (8 bits)
    if len(bits) < current_offset + 8:
        print("No hidden files found in the image (not enough bits for number of files).")
        return
    num_files = int("".join(bits[current_offset : current_offset + 8]), 2)
    current_offset += 8

    if num_files == 0:
        print("No hidden files found in the image.")
        return

    print(f"Found {num_files} hidden file(s).")
    
    for i in range(num_files):
        # Read filename length (8 bits)
        if len(bits) < current_offset + 8:
            print(f"Error: Cannot read filename length for file {i+1}.")
            return
        filename_len = int("".join(bits[current_offset : current_offset + 8]), 2)
        current_offset += 8
        
        # Read filename
        filename_end_offset = current_offset + filename_len * 8
        if len(bits) < filename_end_offset:
            print(f"Error: Cannot read filename for file {i+1}.")
            return
        filename_bits = "".join(bits[current_offset : filename_end_offset])
        filename_bytes = bytearray(int(filename_bits[j:j+8], 2) for j in range(0, len(filename_bits), 8))
        try:
            filename = filename_bytes.decode('utf-8')
        except UnicodeDecodeError:
            print(f"Error: Could not decode filename for file {i+1}. Skipping.")
            current_offset = filename_end_offset # Try to advance offset to continue
            continue
        current_offset = filename_end_offset

        # Read data length (64 bits)
        data_len_end_offset = current_offset + 64
        if len(bits) < data_len_end_offset:
            print(f"Error: Cannot read data length for file {i+1}.")
            return
        data_len = int("".join(bits[current_offset : data_len_end_offset]), 2)
        current_offset = data_len_end_offset

        # Read data
        data_end_offset = current_offset + data_len
        if len(bits) < data_end_offset:
            print(f"Error: Cannot read all data for file {i+1}. File may be corrupt.")
            return
        
        binary_data = "".join(bits[current_offset : data_end_offset])
        current_offset = data_end_offset

        output_file_path = os.path.join(output_dir, filename)
        bits_to_file(binary_data, output_file_path)
        print(f"Decoded file '{filename}' written to {output_file_path}")

def list_hidden_files(image_path):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    bits = []
    # Read all pixels, similar to decode function, to ensure all hidden data is covered
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))
            bits.append(str(pixel[0] & 1))
            bits.append(str(pixel[1] & 1))
            bits.append(str(pixel[2] & 1))

    MAGIC_NUMBER = "0101010101010101" # 16 bits
    MAGIC_NUMBER_LEN = len(MAGIC_NUMBER)

    current_offset = 0

    try:
        # Read magic number
        if len(bits) < current_offset + MAGIC_NUMBER_LEN:
            print("No hidden files found in the image (not enough bits for magic number).")
            return
        
        read_magic_number = "".join(bits[current_offset : current_offset + MAGIC_NUMBER_LEN])
        current_offset += MAGIC_NUMBER_LEN

        if read_magic_number != MAGIC_NUMBER:
            print("No hidden files found in the image (magic number mismatch).")
            return

        # Read number of files (8 bits)
        if len(bits) < current_offset + 8:
            print("No hidden files found in the image (not enough bits for number of files).")
            return
        num_files = int("".join(bits[current_offset : current_offset + 8]), 2)
        current_offset += 8

        if num_files == 0:
            print("No hidden files found in the image.")
            return

        print(f"Found {num_files} hidden file(s):")
        
        for i in range(num_files):
            # Read filename length (8 bits)
            if len(bits) < current_offset + 8:
                print(f"Error: Cannot read filename length for file {i+1}.")
                return
            filename_len = int("".join(bits[current_offset : current_offset + 8]), 2)
            current_offset += 8
            
            # Read filename
            filename_end_offset = current_offset + filename_len * 8
            if len(bits) < filename_end_offset:
                print(f"Error: Cannot read filename for file {i+1}.")
                return
            filename_bits = "".join(bits[current_offset : filename_end_offset])
            filename_bytes = bytearray(int(filename_bits[j:j+8], 2) for j in range(0, len(filename_bits), 8))
            filename = filename_bytes.decode('utf-8')
            current_offset = filename_end_offset

            # Read data length (64 bits)
            data_len_end_offset = current_offset + 64
            if len(bits) < data_len_end_offset:
                print(f"Error: Cannot read data length for file {i+1}.")
                return
            data_len_in_bits = int("".join(bits[current_offset : data_len_end_offset]), 2)
            data_len_in_bytes = data_len_in_bits // 8
            current_offset = data_len_end_offset # Advance offset past data length metadata

            # Advance current_offset past the actual file data bits
            data_end_offset = current_offset + data_len_in_bits
            if len(bits) < data_end_offset:
                print(f"Error: Cannot advance past file data for file {i+1}.")
                return
            current_offset = data_end_offset

            print(f"  - {filename} ({data_len_in_bytes} bytes)")

    except (UnicodeDecodeError, ValueError) as e:
        print(f"No hidden files found in the image or metadata is corrupt: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Encode: python steg.py e <input_image.png> <file1> [file2 ...]")
        print("  Encode: python steg.py e <input_image.png> <output_image.png> <file1> [file2 ...]")
        print("  Decode: python steg.py d encoded.png [output_directory]")
        print("  List:   python steg.py l encoded.png")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'e':
        if len(sys.argv) < 4: # Minimum: e input_img file1
            print("Usage:")
            print("  Encode: python steg.py e <input_image.png> <file1> [file2 ...]")
            print("  Encode: python steg.py e <input_image.png> <output_image.png> <file1> [file2 ...]")
            sys.exit(1)
        
        input_img = sys.argv[2]
        
        # Check if the third argument is an output image path or the first file
        # We assume output image path will have a common image extension
        possible_output_img = sys.argv[3]
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']
        
        if any(possible_output_img.lower().endswith(ext) for ext in image_extensions):
            output_img = possible_output_img
            file_paths = sys.argv[4:]
            if not file_paths: # If output_img was provided but no files
                print("Error: No files provided to hide.")
                sys.exit(1)
        else: # Third argument is the first file, auto-generate output image
            output_img = input_img.replace(".png", "_encoded.png")
            file_paths = sys.argv[3:] # All arguments from 3 onwards are files
        
        encode(input_img, output_img, file_paths)

    elif mode == 'd':
        if len(sys.argv) not in [3, 4]:
            print("Usage: python steg.py d encoded.png [output_directory]")
            sys.exit(1)
        
        encoded_img = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) == 4 else "."
        decode(encoded_img, output_dir)

    elif mode == 'l':
        if len(sys.argv) != 3:
            print("Usage: python steg.py l encoded.png")
            sys.exit(1)
        _, _, encoded_img = sys.argv
        list_hidden_files(encoded_img)

    else:
        print("Invalid mode. Use 'e' for encode, 'd' for decode, or 'l' for list.")
        sys.exit(1)