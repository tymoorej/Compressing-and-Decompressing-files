'''
---------------------------------------------------
| Assignment 2                                    |
| Names: Nathan Douglas Klapstein, Tymoore Jamal  |
| IDs: 1449872 (Nathan), 1452978 (Tymoore)        |
| CMPUT 275 LBL EB2 (Nathan) / EB1 (Tymoore)      |
---------------------------------------------------
'''
import bitio
import huffman
import sys
sys.setrecursionlimit(10000)


def read_tree(bitreader):
    '''Read a description of a Huffman tree from the given bit reader,
    and construct and return the tree. When this function returns, the
    bit reader should be ready to read the next bit immediately
    following the tree description.

    Huffman trees are stored in the following format:
      * TreeLeafEndMessage is represented by the two bits 00.
      * TreeLeaf is represented by the two bits 01, followed by 8 bits
          for the symbol at that leaf.
      * TreeBranch is represented by the single bit 1, followed by a
          description of the left subtree and then the right subtree.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.

    Returns:
      A Huffman tree constructed according to the given description.
    '''
    # read a bit to start bit decision process
    r_bit = bitreader.readbit()

    if r_bit == 1:  # found a branch "1"
        # Recursive in to read_tree to make branch
        left = read_tree(bitreader)
        right = read_tree(bitreader)

        # return found branch
        return huffman.TreeBranch(left, right)
        # program end after all recusions

    if r_bit == 0:  # need to read another bit to figure out what to do
        r_bit = bitreader.readbit()

        if r_bit == 1:  # found a TreeLeaf byte value "01"
            return huffman.TreeLeaf(bitreader.readbits(8))

        elif r_bit == 0:  # TreeLeafEndMessage found  "00"
            return huffman.TreeLeafEndMessage()


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.

    '''
    # grab the compressed stream to be used as bit input stream
    in_stream = bitio.BitReader(compressed)
    # grab compressed message
    # grab the decode tree from the bitstream
    decode_tree = read_tree(in_stream)
    # output list to be appended byte values representing characters
    tree_msg_o = []

    # loop that decodes the rest of the input stream and populates tree_msg_o
    while True:
        # grab the message returned from the decode tree and bitstream input
        tree_msg_r = huffman.decode(decode_tree, in_stream)

        # if the end of message chr was found stop reading and exit loop
        if tree_msg_r == None:
            break
        # save the returned message to to the ouput list for later output
        tree_msg_o.append(tree_msg_r)

    # write message back
    # grab the uncompressed stream to write message back as bit output stream
    out_stream = bitio.BitWriter(uncompressed)

    i = 0
    # loop that writes all the byte values of tree_msg_o to the output stream
    while i < len(tree_msg_o):
        out_stream.writebits(tree_msg_o[i], 8)
        i += 1


def write_tree(tree, bitwriter):
    '''Write the specified Huffman tree to the given bit writer.  The
    tree is written in the format described above for the read_tree
    function.

    DO NOT flush the bit writer after writing the tree.

    Args:
      tree: A Huffman tree.
      bitwriter: An instance of bitio.BitWriter to write the tree to.
    '''

    def enter_tree(tree):

        try:
            # try to grab the TreeLeaf's value
            tree_value = tree.value

            # if code has advanced this far we have hit a TreeLeaf
            # write leaf symbol
            bitwriter.writebit(0)
            bitwriter.writebit(1)

            # write the symbol that was stored in leaf
            bitwriter.writebits(tree_value, 8)

        except AttributeError:
            try:
                # try to grab the TreeBranch's values
                left_tree = tree.left
                right_tree = tree.right

                # if code has advanced this far we have hit a TreeBranch
                # write branch symbol
                bitwriter.writebit(1)

                # enter recusively to solve for branch values
                enter_tree(left_tree)
                enter_tree(right_tree)

            except AttributeError:
                # if code has advanced this far we have hit a TreeLeafEndMessage
                # write TreeLeafEndMessage symbol
                bitwriter.writebit(0)
                bitwriter.writebit(0)

    enter_tree(tree)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''

    # grab the compressed stream to be used as compressed message output stream
    c_stream = bitio.BitWriter(compressed)

    # write encode tree to compressed stream
    write_tree(tree, c_stream)

    # grab the uncompressed stream to use as message input stream
    uc_stream = bitio.BitReader(uncompressed)

    # grab the tree encoding table
    tree_table = huffman.make_encoding_table(tree)

    while True:
        try:
            # grab a byte from the uncompressed stream to encode
            uc_input = uc_stream.readbits(8)

            # grab the encode path list (should be list of trues and falses)
            encoded_input_list = list(tree_table[uc_input])

            # travese this list and for Trues write 1s to compressed stream
            # for falses write 0 to the compressed stream
            for k in list(encoded_input_list):
                if k == True:
                    c_stream.writebit(1)
                else:
                    c_stream.writebit(0)

        except EOFError:  # if we run out of byte values were at the end
            # write the end of message character
            for k in list(tree_table[None]):
                if k == True:
                    c_stream.writebit(1)
                else:
                    c_stream.writebit(0)

            # flush stream for good measure
            c_stream.flush()
            break


# End of File
