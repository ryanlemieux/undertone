# Undertone

Going to write a Go version of this!

This python script encrypts any binary file using any arbitrary binary file as the encryption key. The encrypted file is called an "undertone".

## Usage

To encrypt a file:

>python undertone.py --encrypt binary_key_file binary_file_to_encrypt >> message.und

To decrypt a file:

>python undertone.py --decrypt binary_key_file message.und >> output_file

URLs can also be used to point to key files, undertones, and files to be encrypted.

### How It Works

When encrypting, the script first reads in every byte of the binary key file specified, placing them in a list. Next, the script looks at each byte in the file to be encrypted, and searches for a matching byte in the byte list of the key file. When a match is found, the index of the byte in the list is added to a list. This list of byte locations that is created is the encrypted message (we will call it an "undertone" file).

When decrypting, the script again reads in every byte of the binary key file specified, placing them in a list. The undertone file (encrypted message) is then read, and the bytes that correspond to the index positions in the undertone file are output. If the correct key file was used to decrypt the undertone, the orginal input file will be output.

No byte index from the key file is ever used more than once, thus hampering frequency analysis. The undertone (encrypted message) always consists of a list of unique integers.

The file that is to be encrypted is first compressed with zlib to help reduce the size of the undertone, and is decompressed upon decryption.

