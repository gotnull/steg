# Steganography Tool

A simple Python script for hiding files within images (steganography).

## Description

This tool allows you to encode a file into a PNG image and decode it back. It uses the least significant bit (LSB) of each color channel (RGB) to store the data of the hidden file. It also stores the filename and size of the hidden file, allowing you to list the contents of an encoded image.

## Usage

### Encoding

To hide a file within an image:

```bash
python3 steg.py e <input_image.png> <file_to_hide>
# Or, to specify an output image:
python3 steg.py e <input_image.png> <output_image.png> <file_to_hide>
```

- `<input_image.png>`: The cover image in which you want to hide the file.
- `<file_to_hide>`: The file you want to hide.
- `<output_image.png>`: (Optional) The name of the output image that will contain the hidden file. If not provided, the output image will be named `<input_image_encoded.png>`.

### Listing Hidden Files

To see what file is hidden inside an image:

```bash
python3 steg.py l <encoded_image.png>
```

- `<encoded_image.png>`: The image that you want to inspect.

This will print the filename and size of the hidden file.

### Decoding

To extract a hidden file from an image:

```bash
python3 steg.py d <encoded_image.png> [output_file]
```

- `<encoded_image.png>`: The image that contains the hidden file.
- `[output_file]`: (Optional) The name of the file to which the hidden data will be written. If not provided, the original filename will be used.

## Installation

1.  Clone the repository or download the `steg.py` script.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```
