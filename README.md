Python environment

pip install cryptography

To test the program: 

python rsa_file.py encrypt my_file.docm

expected output:

\u6b63\u5728\u751f\u6210 RSA \u5bc6\u94a5\u5bf9\uff08\u4ec5\u9996\u6b21\u8fd0\u884c\uff09...
\u5bc6\u94a5\u5bf9\u751f\u6210\u5b8c\u6210\uff01private_key.pem \u548c public_key.pem \u5df2\u4fdd\u5b58
\u2705 \u52a0\u5bc6\u5b8c\u6210\uff01
\u52a0\u5bc6\u6587\u4ef6\uff1a./rsa_my_file.docm

python rsa_file.py decrypt rsa_my_file.docm

expected output:.

/my_file.docm
\u2705 \u89e3\u5bc6\u5b8c\u6210\uff01
\u89e3\u5bc6\u6587\u4ef6\uff1a./my_file.docm
