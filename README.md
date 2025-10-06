# Steganography Tool

A simple Python script for hiding multiple files within images (steganography) and extracting them.

## Description

This tool allows you to encode one or more files into a PNG image and decode them back. It uses the least significant bit (LSB) of each color channel (RGB) to store the data of the hidden files. To ensure robust detection, a magic number is embedded, and the tool includes a capacity check to prevent embedding data that exceeds the image's storage limits. It stores the filenames and sizes of the hidden files, allowing you to list the contents of an encoded image.

## Usage

### Encoding

To hide one or more files within an image:

```bash
# Encode a single file, output image name will be auto-generated (e.g., input_image_encoded.png)
python3 steg.py e <input_image.png> <file_to_hide>

# Encode multiple files, output image name will be auto-generated
python3 steg.py e <input_image.png> <file1> <file2> [file3 ...]

# Encode one or more files, specifying the output image name
python3 steg.py e <input_image.png> <output_image.png> <file1> [file2 ...]
```

- `<input_image.png>`: The cover image in which you want to hide the files.
- `<output_image.png>`: (Optional) The name of the output image that will contain the hidden files. If not provided, the output image will be named `<input_image_encoded.png>`.
- `<file1> [file2 ...]`: One or more files you want to hide.

### Listing Hidden Files

To see what files are hidden inside an image:

```bash
python3 steg.py l <encoded_image.png>
```

- `<encoded_image.png>`: The image that you want to inspect.

This will print the filenames and sizes of all hidden files. If no hidden files are detected (e.g., the image is not encoded or corrupted), a friendly message will be displayed.

### Decoding

To extract hidden files from an image:

```bash
python3 steg.py d <encoded_image.png> [output_directory]
```

- `<encoded_image.png>`: The image that contains the hidden files.
- `[output_directory]`: (Optional) The directory where the hidden files will be extracted. If not provided, files will be extracted to the current directory.

## Installation

1.  Clone the repository or download the `steg.py` script.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```