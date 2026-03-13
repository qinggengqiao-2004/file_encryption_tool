import os
import sys
import secrets
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def generate_keys():
    """如果不存在密钥文件，自动生成 2048 位 RSA 密钥对"""
    if os.path.exists("private_key.pem") and os.path.exists("public_key.pem"):
        return
    
    print("正在生成 RSA 密钥对（仅首次运行）...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    # 保存私钥（无密码）
    with open("private_key.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # 保存公钥
    with open("public_key.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print("密钥对生成完成！private_key.pem 和 public_key.pem 已保存")


def load_public_key():
    with open("public_key.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())


def load_private_key():
    with open("private_key.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def encrypt_file(input_path: str, output_path: str):
    """RSA 加密文件（混合加密）"""
    generate_keys()
    public_key = load_public_key()

    # 1. 生成随机 AES-256 密钥
    aes_key = secrets.token_bytes(32)

    # 2. 用 RSA 公钥加密 AES 密钥
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 3. 用 AES-GCM 加密文件内容（支持流式处理，大文件也不会爆内存）
    iv = secrets.token_bytes(12)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()

    with open(output_path, "wb") as outfile:
        # 写入加密后的 AES 密钥（固定 256 字节）和 IV
        outfile.write(encrypted_aes_key)
        outfile.write(iv)

        # 流式读取并加密原文件
        with open(input_path, "rb") as infile:
            while chunk := infile.read(64 * 1024):  # 64KB 缓冲
                outfile.write(encryptor.update(chunk))
        
        # 写入最终密文和认证标签
        outfile.write(encryptor.finalize())
        outfile.write(encryptor.tag)

    print(f"✅ 加密完成！\n加密文件：{output_path}")


def decrypt_file(encrypted_path: str, output_path: str):
    """RSA 解密文件"""
    if not os.path.exists("private_key.pem"):
        print("❌ 私钥文件 private_key.pem 不存在，无法解密！")
        return

    private_key = load_private_key()

    with open(encrypted_path, "rb") as f:
        encrypted_aes_key = f.read(256)   # RSA 2048 位加密后的 AES 密钥长度固定
        iv = f.read(12)
        remaining = f.read()

    # 拆分密文和标签
    if len(remaining) < 16:
        print("❌ 文件格式错误！")
        return
    ciphertext = remaining[:-16]
    tag = remaining[-16:]

    # 1. 用 RSA 私钥解密 AES 密钥
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 2. 用 AES-GCM 解密
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    with open(output_path, "wb") as f:
        f.write(plaintext)

    print(f"✅ 解密完成！\n解密文件：{output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法：")
        print("  加密：python rsa_file.py encrypt 文件路径")
        print("  解密：python rsa_file.py decrypt 加密文件路径 [输出文件名]")
        print("\n示例：")
        print("  python rsa_file.py encrypt photo.jpg")
        print("  python rsa_file.py decrypt rsa_photo.jpg")
        sys.exit(1)

    mode = sys.argv[1].lower()
    input_file = sys.argv[2]

    if os.path.exists(input_file):
        # 自动生成输出文件名
        if mode == "encrypt":
            base_name = os.path.basename(input_file)
            output_file = os.path.join(os.path.dirname(input_file) or ".", f"rsa_{base_name}")
            encrypt_file(input_file, output_file)
        
        elif mode == "decrypt":
            # 如果输入是 rsa_ 开头，自动去掉前缀
            base_name = os.path.basename(input_file)
            if base_name.startswith("rsa_"):
                orig_name = base_name[4:]
            else:
                orig_name = "decrypted_" + base_name
            output_file = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(input_file) or ".", orig_name)
            print(output_file)
            decrypt_file(input_file, output_file)
        
        else:
            print("❌ 模式只能是 encrypt 或 decrypt")
    else:
        print("文件不存在")