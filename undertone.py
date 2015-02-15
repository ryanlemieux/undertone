#!/usr/bin/env python3.4
#
# Undertone v1.1 alpha
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

__version__ = '1.1a'

__author__ = 'Ryan Lemieux'

import sys, argparse, os, random, zlib, re
import urllib.request
from urllib.parse import urlparse
from bitstring import bitstring

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--encrypt',action='append',nargs=2,metavar=('keyfile','message'))
    parser.add_argument('--decrypt',action='append',nargs=2,metavar=('keyfile','undertone'))
    args = parser.parse_args()

    if args.encrypt:

        keyfile = args.encrypt[0][0]
        message_location = args.encrypt[0][1]

        #   Fetch file if URL specified as message input:
        if re.match('(http)',message_location):
            message_location = fetch_url(message_location)

        with open(message_location,'rb') as message_file:

            message = bytearray(message_file.read())

            #   Create byte and location dictionaries from keyfile:
            keyfile_dicts = process_keyfile(keyfile)

            #   Convert message to list of byte locations:
            undertone = create_undertone(keyfile_dicts, message)

            print(undertone)

    elif args.decrypt:

        keyfile = args.decrypt[0][0]
        decrypted_msg = ""
        decompressed_crypt = ""

        with open(str(args.decrypt[0][1]),'r') as undertone_file:

            undertone = undertone_file.read()
            keyfile_dicts = process_keyfile(keyfile)
            decrypted_msg = decrypt_msg(keyfile_dicts,undertone)
            sys.stdout.buffer.write(decrypted_msg)
    else:
        parser.print_help()

def process_keyfile(keyfile):

    bytes_dict = {}
    locations_dict = {}
    byte_location = 0
    keyfile_dicts = []

    with open(keyfile, "rb") as chunk:

        byte = chunk.read(1)

        while byte:
            if byte not in bytes_dict:
                location_list = [byte_location]
                bytes_dict[byte] = location_list
            else:
                bytes_dict[byte] += [byte_location]

            locations_dict[byte_location] = byte
            byte = chunk.read(1)
            byte_location += 1

    keyfile_dicts = [bytes_dict,locations_dict]
    return keyfile_dicts

def create_undertone(keyfile_dicts, message):

    encrypted_msg = ''
    bytes_dict = keyfile_dicts[0]

    for byte in message:

        byte = bytes([byte])

        #   In the event of no byte available in the bytes_dict dict,
        #   simply omit the byte from the string, and print a warning
        #   message.

        #   The byte could be in the dictionary but still have an empty
        #   position list, as this algorithm removes byte positions as they
        #   are used. So we have to check the length of the list, rather than
        #   just seeing if the byte is in the dictionary.
        if len(bytes_dict[byte]) > 0:

            random_byte_loc = random.choice(bytes_dict[byte])
            encrypted_msg += str(random_byte_loc) + '\n'

            #   Remove used byte location from list to prevent the
            #   duplicate use of the byte location, thus hampering
            #   frequency analysis.
            bytes_dict[byte].remove(random_byte_loc)

        else:
            print('WARNING: Not enough bytes in pool: Omitting' +
            ' byte.\nRemedy: Use a larger keyfile.\n')

    return encrypted_msg

def decrypt_msg(keyfile_dicts,crypt_msg):

    decrypted_msg = bytearray()
    locations_dict = keyfile_dicts[1]

    for location in crypt_msg.split('\n'):
        if location !=  '':
            if int(location) in locations_dict: # Fail silently...
                decrypted_msg += locations_dict[int(location)]

    return decrypted_msg

def fetch_url(url):

    temp_dir = "temp"
    url_path = urllib.parse.urlparse(url)[2].split('/')
    file_name = url_path[len(url_path) - 1]
    file_path = temp_dir + '/' + file_name

    # TO DO: Proper try blocks here:

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    urllib.request.urlretrieve(url,file_path)

    return file_path

if __name__ == "__main__":
    main(sys.argv)

