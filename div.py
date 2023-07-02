import argparse
import math
import sys

MAGIC_STRING = "division_compression.pyable"
BYTE_ORDER = "big"
BYTE_SIGNED = False
STRING_ENCODING = "utf-8"
LENGTH_INDICATOR_BYTES = 16
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

if args.command == "compress":
    f = open(args.file, "rb")

    file_bytes = f.read()
    num = int.from_bytes(file_bytes, BYTE_ORDER, signed=BYTE_SIGNED)

    divisor = num // math.floor(len(file_bytes) * 0.5)
    rounded_result = num // divisor
    remainder = num % divisor

    print(divisor)

    f.close()

    out_file = args.output_file

    if out_file is None:
        out_file = args.file + COMPRESSED_FILE_EXTENSION

    f = open(out_file, "wb")

    divisor_bytes = divisor.to_bytes(byte_length(divisor), BYTE_ORDER, signed=BYTE_SIGNED)
    rounded_result_bytes = rounded_result.to_bytes(byte_length(rounded_result), BYTE_ORDER, signed=BYTE_SIGNED)
    remainder_bytes = remainder.to_bytes(byte_length(remainder), BYTE_ORDER, signed=BYTE_SIGNED)

    f.write(MAGIC_STRING.encode(STRING_ENCODING))

    f.write(len(divisor_bytes).to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED))
    f.write(divisor_bytes)

    f.write(len(rounded_result_bytes).to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED))
    f.write(rounded_result_bytes)

    f.write(len(remainder_bytes).to_bytes(LENGTH_INDICATOR_BYTES, BYTE_ORDER, signed=BYTE_SIGNED))
    f.write(remainder_bytes)
    
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

    divisor_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)
    divisor = int.from_bytes(f.read(divisor_length), BYTE_ORDER, signed=BYTE_SIGNED)

    rounded_result_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)
    rounded_result = int.from_bytes(f.read(rounded_result_length), BYTE_ORDER, signed=BYTE_SIGNED)

    remainder_length = int.from_bytes(f.read(LENGTH_INDICATOR_BYTES), BYTE_ORDER, signed=BYTE_SIGNED)
    remainder = int.from_bytes(f.read(remainder_length), BYTE_ORDER, signed=BYTE_SIGNED)

    decompressed = rounded_result * divisor + remainder
    decompressed_bytes = decompressed.to_bytes(byte_length(decompressed), BYTE_ORDER, signed=BYTE_SIGNED)

    f.close()

    out_file = args.output_file

    if out_file is None:
        out_file = args.file + DECOMPRESSED_FILE_EXTENSION

    f = open(out_file, "wb")

    f.write(decompressed_bytes)

    f.flush()
    f.close()