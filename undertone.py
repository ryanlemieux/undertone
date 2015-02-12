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

    input = argv[1]
    byte_location = 0
    ascii_chars = {}
    locations = {}

    with open(input, "rb") as chunk:
        byte = chunk.read(1)
        while byte:
            if str(byte) not in ascii_chars:
                location_list = [byte_location]
                ascii_chars[str(byte)] = location_list
            else:
                ascii_chars[str(byte)] += [byte_location]

            locations[byte_location] = str(byte)
            byte = chunk.read(1)
            byte_location += 1

    encrypted_msg = []

    for char in argv[2]:
        random_char_loc = random.choice(ascii_chars[char])
        encrypted_msg += [random_char_loc]
        # Remove used char loc. from list to avoid duplicate char loc. use
        ascii_chars[char].remove(random_char_loc)


    crypt_string = ""

    for location in encrypted_msg:
        crypt_string += str(location) + '\n'

    compressed_crypt = zlib.compress(crypt_string)

    print(encrypted_msg)
    print
    print crypt_string
    print
    print compressed_crypt

    decompressed_crypt = zlib.decompress(compressed_crypt)
    decrypted_msg = ""

    for location in decompressed_crypt.split('\n'):
        if location !=  '':
            decrypted_msg += locations[int(location)]

    file = open('crypt.msg', 'w')

    try:
        file.write(compressed_crypt)
    finally: file.close()

    print decompressed_crypt
    print decrypted_msg

    print   # pretty terminal newline

if __name__ == "__main__":
    main(sys.argv)

