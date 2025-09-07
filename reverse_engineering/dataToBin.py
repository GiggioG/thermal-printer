import os
import glob

os.makedirs("databin", exist_ok=True)

for data_file in glob.glob("data/data*.txt"):
    with open(data_file, "r") as f:
        hex_data = f.read().replace('\n', '').replace(' ', '')

    # Convert hex string to bytes
    byte_data = bytes.fromhex(hex_data)

    # Generate output filename: databin/data#.bin
    base = os.path.splitext(os.path.basename(data_file))[0]
    out_file = f"databin/{base}.bin"

    with open(out_file, "wb") as fout:
        fout.write(byte_data)