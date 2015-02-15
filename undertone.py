#!/usr/bin/env python3.4
#
# Undertone v2.0 alpha
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

__version__ = '2.0a'

__author__ = 'Ryan Lemieux'

import sys, argparse, random, zlib, re
import urllib.request
from urllib.parse import urlparse

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--encrypt',action='append',
                        nargs=2,metavar=('keyfile','message'))
    parser.add_argument('--decrypt',action='append',
                        nargs=2,metavar=('keyfile','undertone'))
    args = parser.parse_args()

    if args.encrypt:

        keyfile = get_file(args.encrypt[0][0])
        message = get_file(args.encrypt[0][1])
        keyfile_dicts = process_keyfile(keyfile)
        undertone = create_undertone(keyfile_dicts, message)
        
        if undertone:
            print(undertone)

    elif args.decrypt:

        keyfile = get_file(args.decrypt[0][0])
        undertone = get_file(args.decrypt[0][1],'r')
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

    for byte in keyfile:

        byte = bytes([byte])

        if byte not in bytes_dict:
            location_list = [byte_location]
            bytes_dict[byte] = location_list
        else:
            bytes_dict[byte] += [byte_location]

        locations_dict[byte_location] = byte
        byte_location += 1

    keyfile_dicts = [bytes_dict,locations_dict]
    return keyfile_dicts

def create_undertone(keyfile_dicts, message):

    encrypted_msg = ''
    bytes_dict = keyfile_dicts[0]
    #   Compress the file before encryption:
    message = zlib.compress(message)

    for byte in message:

        byte = bytes([byte])

        #   The byte could be in the dictionary but still have an empty
        #   position list, as this algorithm removes byte positions as they
        #   are used. So we have to check the length of the list, rather than
        #   just seeing if the byte is in the dictionary.
        if byte in bytes_dict and len(bytes_dict[byte]) > 0:

            #   Randomize the location choice so that the same character is
            #   not fetched in a linear fashion going through the file.
            random_byte_loc = random.choice(bytes_dict[byte])
            encrypted_msg += str(random_byte_loc) + '\n'

            #   Remove used byte location from list to prevent the
            #   duplicate use of the byte location, thus hampering
            #   frequency analysis.
            bytes_dict[byte].remove(random_byte_loc)

        else:
            #   Running out of bytes from the keyfile pool is a fatal error.
            print('\nERROR: Not enough bytes in pool!\n' +
                    'Remedy: Use a larger keyfile.\n')

            return None

    return encrypted_msg

def decrypt_msg(keyfile_dicts,crypt_msg):

    decrypted_msg = bytearray()
    locations_dict = keyfile_dicts[1]

    for location in crypt_msg.split('\n'):
        if location !=  '':
            if int(location) in locations_dict: # Fail silently...
                decrypted_msg += locations_dict[int(location)]

    #   Don't forget to decompress the message:
    return zlib.decompress(decrypted_msg)

def get_file(path,mode='rb'):
    #   Fetch file if URL specified as keyfile input:
    if re.match('(http)',path):
        input_file = fetch_url(path)

        if mode == 'r':
            input_file = input_file.decode('UTF-8')
    else:
        with open(path,mode) as file_path:
            input_file = file_path.read()

    return input_file

def fetch_url(url):

    return urllib.request.urlopen(url).read()

if __name__ == "__main__":
    main(sys.argv)

