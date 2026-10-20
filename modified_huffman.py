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
    
    # def __repr__(self):
    #     print(f"{self.Symbol}, {self.Frequency}\n")


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
def codes_table_construction(root: Node, path: str = ' '):
    if root is None:
        return

    if root.left_child is None and root.right_child is None:
        root.code = path
        codes_list.append(root)
        return
    
    codes_table_construction(root.left_child, path + '0')
    codes_table_construction(root.right_child, path + '1')


def Huffman_Compress(user_input: str):
    root = Huffman_Tree_Construction(user_input)
    codes_table_construction(root)
    compressed: str = ""

    for char in user_input:
        for node in codes_list:
            if char == node.Symbol:
                compressed += node.code

    return compressed

def Huffman_Decompress(compressed: str):
    decompressed: str = ""
    current_code: str = ""

    for bit in compressed:
        current_code += bit

        for node in codes_list:
            if current_code == node.code:
                decompressed += node.Symbol
                current_code = ""
                break

    return decompressed


codes_list = []


import os
folder_path = r"C:\Users\Youssef Ansary\Desktop\College\Assignments\Info and Compression"
file_path = os.path.join(folder_path, "input.txt")

choice = int(input("1. Compress\n2. Decompress: "))

if choice == 1:
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    compressed_bits = Huffman_Compress(file_content)

    output_text = f"Compressed string :\n{compressed_bits}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print("File updated successfully.")
    
else:
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    print("Decompressed output:")
    print(Huffman_Decompress(file_content))
