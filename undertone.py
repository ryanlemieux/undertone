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

import sys, os, random, zlib

def main(argv):

    if len(argv) >= 4:

        action = argv[1]
        binary_chunk = argv[2]
        message = argv[3]

        if str(argv[1]) == 'encrypt':

            #   Use input message file in specified:
            if message == '-f' and len(argv) == 5:
                message_file = open(str(argv[4]),'rb')
                message = message_file.read()

            # Create ascii_chars and locations dictionaries from binary chunk:
            key_dicts = process_chunk(binary_chunk)
            ascii_chars = key_dicts[0]

            #   Convert message to list of char locations:
            encrypted_msg = ""

            for char in message:

                #   In the event of no char available in the ascii_chars dict,
                #   simply omit the char from the string, and print a warning
                #   message.
                if len(ascii_chars[char]) > 0:

                    random_char_loc = random.choice(ascii_chars[char])
                    encrypted_msg += str(random_char_loc) + '\n'

                    #   Remove used char location from list to prevent the
                    #   duplicate use of the char location, thus hampering
                    #   frequency analysis.
                    ascii_chars[char].remove(random_char_loc)

                else:
                    print ('WARNING: Not enough characters in pool: Omitting' +
                    ' character.\nRemedy: Use a larger binary input file.\n')

            # Compress encrypted_msg with zlib and write to file crypt.msg:
            compressed_crypt = zlib.compress(encrypted_msg)
            file = open('crypt.msg', 'wb')

            try:
                file.write(compressed_crypt)
            finally:
                file.close()

        elif str(argv[1]) == 'decrypt':

            decrypted_msg = ""
            decompressed_crypt = ""
            #   Using this zlib.decompressobj() allows silent decryption of
            #   corrupted or incomplete compressed data.
            decompressor = zlib.decompressobj()
            file = open(str(message),'rb')
            # Create ascii_chars and locations dictionaries from binary chunk:
            key_dicts = process_chunk(binary_chunk)

            try:
                decompressed_crypt = decompressor.decompress(file.read())
            finally:
                file.close()

                decrypted_msg = decrypt_msg(key_dicts,decompressed_crypt)

            #   Write to output file if specified:
            if len(argv) > 5 and argv[4] == '-o':

                file = open(argv[5], 'wb')

                try:
                    file.write(decrypted_msg)
                finally:
                    file.close()
            else:
                print '\n' + decrypted_msg + '\n'
        else:
            print ('\nERROR: First argument must be either \'encrypt\' or ' +
                    '\'decrypt\'.\n')
    else:
        print ('\nERROR: Too few command line arguments. Typical use:\n\n' +
            'Encrypt: python undertone.py encrypt anyfile -f message\n' +
        'Decrypt: python undertone.py decrypt anyfile crypt.msg -o output\n')

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
                #   Encoding to base36 slightly reduces encrypted msg filesize
                ascii_chars[str(byte)] += [base36encode(byte_location)]

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
            if base36decode(location) in locations_dict: # Fail silently...
                decrypted_msg += locations_dict[int(base36decode(location))]

    return decrypted_msg

def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):

    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number,len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36

def base36decode(number):
    return int(number,36)

if __name__ == "__main__":
    main(sys.argv)

