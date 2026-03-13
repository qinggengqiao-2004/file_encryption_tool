Python environment

pip install cryptography

To test the program: 

python rsa_file.py encrypt my_file.docm


python rsa_file.py decrypt rsa_my_file.docm

expected output (encrypt) :

正在生成 RSA 密钥对（仅首次运行）...

密钥对生成完成！private_key.pem 和 public_key.pem 已保存

✅ 加密完成！

加密文件：./rsa_my_file.docm

expected output (decrypt) :

./my_file.docm

✅ 解密完成！

解密文件：./my_file.docm
