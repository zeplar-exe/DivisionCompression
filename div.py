import argparse
import math
import sys

MAGIC_STRING = "division_compression.pyable"
BYTE_ORDER = "big"
BYTE_SIGNED = False
STRING_ENCODING = "utf-8"
LENGTH_INDICATOR_BYTES = 128
COMPRESSED_FILE_EXTENSION = ".div"
DECOMPRESSED_FILE_EXTENSION = ".undiv"

parser = argparse.ArgumentParser("Division Compression")
subparsers = parser.add_subparsers(dest="command")

compression_parser = subparsers.add_parser("compress", help="Compress a given file.")
compression_parser.add_argument("file", help="The target file to compress.", type=str)
compression_parser.add_argument('-o', "--output", help=f"The output file. Defaults to the input file with {COMPRESSED_FILE_EXTENSION} at the end.", type=str, default=None, dest="output_file")

decompression_parser = subparsers.add_parser("decompress", help="Decompress a given file.")
decompression_parser.add_argument("file", help="The target file to decompress.", type=str)
decompression_parser.add_argument('-o', "--output", help=f"The output file. Defaults to the input file with {DECOMPRESSED_FILE_EXTENSION} at the end.", type=str, default=None, dest="output_file")

args = parser.parse_args()

def byte_length(n):
    return (n.bit_length() + 7) // 8

def to_base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def from_base(digits, b):
    n = 0
    for d in digits:
        n = b * n + d
    return n

def join_list(list):
    return''.join(map(str, list))

if args.command == "compress":
    f = open(args.file, "rb")

    file_bytes = f.read()
    num = int.from_bytes(file_bytes, BYTE_ORDER, signed=BYTE_SIGNED)

    base = 577
    digits = to_base(num, base)

    f.close()

    out_file = args.output_file

    if out_file is None:
        out_file = args.file + COMPRESSED_FILE_EXTENSION

    f = open(out_file, "wb")

    f.write(MAGIC_STRING.encode(STRING_ENCODING))

    base_bytes = base.to_bytes(byte_length(base), BYTE_ORDER, signed=BYTE_SIGNED)
    base_length_bytes = len(base_bytes).to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED)

    f.write(base_length_bytes)
    f.write(base_bytes)
    
    digits_length_bytes = len(digits).to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED)
    digit_length = max(map(lambda n : len(str(n)), digits))
    digit_length_bytes = digit_length.to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED)

    print(digit_length)
    print(len(digits))

    f.write(digits_length_bytes)
    f.write(digit_length_bytes)

    for digit in digits:
        digit_bytes = digit.to_bytes(digit_length, BYTE_ORDER, signed=BYTE_SIGNED)
        f.write(digit_bytes)
    
    f.flush()
    f.close()

    print(f"Compression Successful ({args.file} -> {out_file})")
elif args.command == "decompress":
    f = open(args.file, "rb")

    def fail(reason):
        global f
        print("File format error while decompressing: " + reason)
        f.close()
        sys.exit()

    magic = f.read(len(MAGIC_STRING.encode(STRING_ENCODING))).decode(STRING_ENCODING)

    if magic != MAGIC_STRING:
        fail("Magic string missing.")

    base_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)
    base = int.from_bytes(f.read(base_length), BYTE_ORDER, signed=BYTE_SIGNED)
    
    digits_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)
    digit_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)

    digits = []

    for i in range(digits_length):
        digit = int.from_bytes(f.read(digit_length), BYTE_ORDER, signed=BYTE_SIGNED)
        digits.append(digit)

    decompressed = from_base(digits, base)
    decompressed_bytes = decompressed.to_bytes(byte_length(decompressed), BYTE_ORDER, signed=BYTE_SIGNED)

    f.close()

    out_file = args.output_file

    if out_file is None:
        out_file = args.file + DECOMPRESSED_FILE_EXTENSION

    f = open(out_file, "wb")

    f.write(decompressed_bytes)

    f.flush()
    f.close()