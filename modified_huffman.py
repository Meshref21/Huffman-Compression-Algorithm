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


def Huffman_Tree_Construction(user_input: str):
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

    while len(freq_table) >= 2:
        # sort based on the node's freq (ASCENDING)
        list.sort(freq_table, key=lambda node: node.Frequency)
        parent_node = Node(None, freq_table[0].Frequency + freq_table[1].Frequency)
        parent_node.add_childs(freq_table[0], freq_table[1])
        freq_table.pop(0)
        freq_table.pop(0)
        freq_table.append(parent_node)

    root: Node = freq_table[0]

    return root

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

def Huffman_Compress(user_input: str):


    root = Huffman_Tree_Construction(user_input)
    codes_list = codes_table_construction(root)
    
    #debug only============================= DELETE LATER
    for node in codes_list:
        print(f"symbol: {node.Symbol}, code: {node.code}\n")
    #debug only============================= DELETE LATER

    # only unique character
    if len(codes_list) == 1 and codes_list[0].code == "":
        codes_list[0].code = '0'

    codes_table = {}

    for node in codes_list:
        codes_table[node.Symbol] = node.code

    
    compressed: str = ""

    for char in user_input:
        compressed += codes_table[char]

    return {
        "codes": codes_table,
        "compressed": compressed
    }

def Huffman_Decompress(compressed, codes_table):

    reverse_codes = {}

    for symbol, code in codes_table.items():
        reverse_codes[code] = symbol

    decompressed = ""
    current_code = ""

    for bit in compressed:
        current_code += bit

        if current_code in reverse_codes:
            decompressed += reverse_codes[current_code]
            current_code = ""


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


import os, json, math


folder_path = r"/home/mido/Documents/"
file_path = os.path.join(folder_path, "input.txt")

choice = int(input("1. Compress\n2. Decompress: "))

if choice == 1:
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read().rstrip('\n') # removing trailing new line form the right
    data = Huffman_Compress(file_content)

    packed, bit_length = pack_bits(data["compressed"])
    print(repr(packed))
    print(repr(bit_length))
    with open("compressed.bin", "wb") as f:
        f.write(packed)

    output_text = f"\n{data["compressed"]}"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data["codes"], f, ensure_ascii=True)
        f.write(output_text)

    print_compression_statistics(file_content, data["compressed"], file_path)
    print("File updated successfully.")
    
else:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    codes_table = json.loads(lines[0])
    compressed = lines[1].strip()

    decompressed_text = Huffman_Decompress(compressed, codes_table)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(decompressed_text)

