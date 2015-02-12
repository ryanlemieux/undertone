#!/usr/bin/env python
#
# Undertone v1.0 alpha
#
# Copyright (C) 2015 Ryan Lemieux <ryans.email.2@gmail.com>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detail.
#
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

import sys, os, random, hashlib, zlib

def main(argv):

    if len(argv) == 4:

        action = argv[1]
        binary_chunk = argv[2]
        message = argv[3]
        # Create ascii_chars and locations dictionaries from binary chunk:
        key_dicts = process_chunk(binary_chunk)

        if str(argv[1]) == 'encrypt':

            ascii_chars = key_dicts[0]

            # Convert message to list of char locations:
            encrypted_msg = ""

            for char in message:

                #   In the event of no char available in the ascii_chars dict,
                #   fail silently by simply omitting the character from the
                #   message.
                if len(ascii_chars[char]) > 0:

                    random_char_loc = random.choice(ascii_chars[char])
                    encrypted_msg += str(random_char_loc) + '\n'
                    # Remove used char loc. from list to avoid duplicate char loc. use
                    ascii_chars[char].remove(random_char_loc)

                else:
                    print ('Not enough characters in pool: Omitting ' +
                    'character.\nRemedy: Use a larger binary input file.\n')

            # Compress encrypted_msg with zlib and write to file crypt.msg:
            compressed_crypt = zlib.compress(encrypted_msg)
            file = open('crypt.msg', 'wb')

            try:
                file.write(compressed_crypt)
            finally:
                file.close()

            #test
            decompressor = zlib.decompressobj()

            decompressed_crypt = decompressor.decompress(compressed_crypt)

            decrypted_msg = decrypt_msg(key_dicts,decompressed_crypt)
            print decrypted_msg
            #test
            print   # pretty terminal newline

        elif str(argv[1]) == 'decrypt':

            #   To do: move the process_chunk() call so it only occurs if all
            #   file exist etc... Currently it parses the whole file before
            #   telling you that your input file is non-existent.
            decrypted_msg = ""
            decompressed_crypt = ""
            #   Using this zlib.decompressobj() allows silent decryption of
            #   corrupted or incomplete compressed data.
            decompressor = zlib.decompressobj()
            file = open(str(message),'rb')

            try:
                #   Note: It's important to use .read() rather than
                #   .readline() ... The encrypted string sometimes gets
                #   corrupted when being read with .readline(). (Not sure why)
                decompressed_crypt = decompressor.decompress(file.read())
            finally:
                file.close()

                decrypted_msg = decrypt_msg(key_dicts,decompressed_crypt)

                print decrypted_msg
        else:
            print ('\nERROR: First argument must be either \'encrypt\' or ' +
                    '\'decrypt\'.\n')
    else:
        print ('\nERROR: Too few command line arguments.\nTypical use: python ' +
                'undertone.py encrypt/decrypt anyfile message.txt/crypt.msg\n')

def process_chunk(binary_chunk):

    ascii_chars = {}
    locations_dict = {}
    byte_location = 0
    key_dicts = []

    with open(binary_chunk, "rb") as chunk:
        byte = chunk.read(1)
        while byte:
            if str(byte) not in ascii_chars:
                location_list = [byte_location]
                ascii_chars[str(byte)] = location_list
            else:
                ascii_chars[str(byte)] += [byte_location]

            locations_dict[byte_location] = str(byte)
            byte = chunk.read(1)
            byte_location += 1

    key_dicts = [ascii_chars,locations_dict]
    return key_dicts

def decrypt_msg(key_dicts,crypt_msg):

    decrypted_msg = ""
    locations_dict = key_dicts[1]

    for location in crypt_msg.split('\n'):
        if location !=  '':
            if int(location) in locations_dict: # Fail silently...
                decrypted_msg += locations_dict[int(location)]

    return decrypted_msg

if __name__ == "__main__":
    main(sys.argv)

