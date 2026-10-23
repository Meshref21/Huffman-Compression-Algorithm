class Node:
    def __init__(self, Symbol: str, Frequency: int):
        self.Symbol = Symbol
        self.Frequency = Frequency
        self.code = None
        self.left_child: Node = None
        self.right_child: Node = None

    def add_childs(self, left_child: Node, right_child: Node):
        self.left_child = left_child
        self.right_child = right_child


def Huffman_Tree_Construction(user_input: str, threshold: int):
    freq_table = []

    for char in user_input:
        found = False
        for node in freq_table: # increase it's freq
            if node.Symbol == char:
                node.Frequency += 1
                found = True
                break
        if not found:            
            current_node = Node(char, 1)
            freq_table.append(current_node)

    others_characters = []

    others_freq = 0
    for node in freq_table[:]:
        if node.Frequency < threshold:
            others_freq += node.Frequency
            others_characters.append(node.Symbol)
            freq_table.remove(node)

    if others_freq > 0:
        freq_table.append(Node("OTHERS", others_freq))

    while len(freq_table) >= 2:
        # sort based on the node's freq (ASCENDING)
        list.sort(freq_table, key=lambda node: node.Frequency)
        parent_node = Node(None, freq_table[0].Frequency + freq_table[1].Frequency)
        parent_node.add_childs(freq_table[0], freq_table[1])
        freq_table.pop(0)
        freq_table.pop(0)
        freq_table.append(parent_node)

    root: Node = freq_table[0]

    return root, others_characters

#preorder traversal through the tree
def codes_table_construction(root: Node, path: str = '', codes_list=None):

    if codes_list is None:
        codes_list = []

    if root is None:
        return codes_list

    if root.left_child is None and root.right_child is None:
        root.code = path
        codes_list.append(root)
        return codes_list
    
    codes_table_construction(root.left_child, path + '0', codes_list)
    codes_table_construction(root.right_child, path + '1', codes_list)

    return codes_list

def others_codes_construction(others_characters: list):
    codes = {}

    if not others_characters:
        return {}

    #if others only contains one character
    number_bits_needed = max(1, math.ceil(math.log2(len(others_characters))))

    for i in range(len(others_characters)):
        char = others_characters[i]
        codes[char] = format(i, f"0{number_bits_needed}b")

    return codes

def Huffman_Compress(user_input: str):


    root, others_characters = Huffman_Tree_Construction(user_input)
    others_codes = others_codes_construction(others_characters)
    codes_list = codes_table_construction(root)
    

    # only unique character
    if len(codes_list) == 1 and codes_list[0].code == "":
        codes_list[0].code = '0'

    codes_table = {}

    for node in codes_list:
        codes_table[node.Symbol] = node.code

    
    compressed: str = ""

    for char in user_input:
        if char in others_codes:
            compressed += codes_table["OTHERS"]
            compressed += others_codes[char]
        else:
            compressed += codes_table[char]

    return {
        "codes": codes_table,
        "compressed": compressed,
        "others_codes": others_codes
    }

def Huffman_Decompress(compressed, codes_table, others_codes):

    reverse_codes = {}

    for symbol, code in codes_table.items():
        reverse_codes[code] = symbol

    reverse_others_codes = {}

    for symbol, code in others_codes.items():
        reverse_others_codes[code] = symbol

    others_bits = max(1, math.ceil(math.log2(len(others_codes))))


    decompressed = ""
    current_code = ""
    i = 0

    while i < len(compressed):
        current_code += compressed[i]
        i += 1

        if current_code in reverse_codes:
            symbol = reverse_codes[current_code]

            if symbol == "OTHERS":
                fixed_code = compressed[i:i + others_bits]
                i += others_bits
                decompressed += reverse_others_codes[fixed_code]
            else:
                decompressed += symbol

            current_code = ""



    # for bit in compressed:
    #     current_code += bit

    #     if current_code in reverse_codes:
    #         decompressed += reverse_codes[current_code]
    #         current_code = ""
            


    return decompressed

def pack_bits(compressed: str) -> tuple[bytes, int]:
    
    bit_length = len(compressed)
    padding = (8 - (len(compressed) % 8)) % 8
    compressed += "0" * padding

    packed = b""

    for i in range(0, len(compressed), 8):
        byte = int(compressed[i:i + 8], 2)
        packed += bytes([byte])

    return packed, bit_length


def unpack_bits(packed: bytes, bit_length: int) -> str:
    bits = ""

    for byte in packed:
        bits += format(byte, "08b")

    return bits[:bit_length]


def print_compression_statistics(original: str, compressed: str, file_path: str):

    original_size = len(original.encode("utf-8")) * 8

    # Theoretical size of compressed bits
    compressed_bits_size = len(compressed)

    # Actual output file size in bits, including the codes table
    actual_file_size = os.path.getsize(file_path) * 8

    print("\n--- Compression Statistics ---")
    print(f"Original size: {original_size} bits")
    print(f"Compressed data size: {compressed_bits_size} bits")
    print(f"Actual compressed file size: {actual_file_size} bits")


import os, json, math, struct


folder_path = r"/home/mido/Documents/"
file_path = os.path.join(folder_path, "input.txt")

choice = int(input("1. Compress\n2. Decompress: "))

if choice == 1:
    threshold = int(input("Enter frequency threshold: "))

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read().rstrip('\n') # removing trailing new line form the right
    data = Huffman_Compress(file_content, threshold)

    packed, bit_length = pack_bits(data["compressed"])

    # convert codes table to bytes then calc it's size and store in the header of the file
    codes_table_bytes = json.dumps(data["codes"]).encode("utf-8")
    codes_table_length = len(codes_table_bytes)


    #store the table length and bit length in the header
    #bit length is used for knowing how many padded bits in the last byte
    with open("compressed.bin", "wb") as f:
        f.write(struct.pack(">I", codes_table_length))
        f.write(struct.pack(">I", bit_length))
        f.write(codes_table_bytes)
        f.write(packed)

        print(repr(codes_table_bytes))
        print(repr(packed))
        print(repr(bit_length))

    print_compression_statistics(file_content, data["compressed"], "compressed.bin")
    print("File updated successfully.")
    
else:
    with open("compressed.bin", "rb") as f:
        
        #read the header
        codes_table_length = struct.unpack(">I", f.read(4))[0]
        bit_length = struct.unpack(">I", f.read(4))[0]

        #read the huffman table
        codes_table_bytes = f.read(codes_table_length)
        codes_table = json.loads(codes_table_bytes.decode("utf-8"))

        packed = f.read()


        print("Table length:", codes_table_length)
        print("Meaningful bits:", bit_length)
        print("Codes table:", codes_table)
        print("Packed data:", packed)

    actual_unpacked_bits = unpack_bits(packed, bit_length)
    decompressed_text = Huffman_Decompress(actual_unpacked_bits, codes_table)


    output_path = os.path.join(folder_path, "decompressed.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(decompressed_text)

    print("File decompressed successfully.")

