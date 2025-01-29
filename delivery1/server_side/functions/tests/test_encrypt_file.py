from cipher import encrypt_file

key = bytes.fromhex('0700d603a1c514e46b6191ba430a3a0c')
iv = bytes.fromhex('aad1583cd91365e3bb2f0c3430d065bb')

encrypt_file('../files/example.txt', key, iv)

#encrypt_file('files/exemplo.pdf', key, iv)