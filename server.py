import socket
import threading
import tkinter as tk
from Crypto.Cipher import AES

key = b"Sixteen byte key"

def encrypt_message(message):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return cipher.nonce + tag + ciphertext

def decrypt_message(data):
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

# GUI Setup
root = tk.Tk()
root.title("Server Chat")

frame = tk.Frame(root)
frame.pack()

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat_area = tk.Text(frame, height=20, width=50, yscrollcommand=scrollbar.set)
chat_area.pack(side=tk.LEFT)
scrollbar.config(command=chat_area.yview)

# Color tags
chat_area.tag_config("blue", foreground="blue")
chat_area.tag_config("red", foreground="red")
chat_area.tag_config("gray", foreground="gray")

msg_entry = tk.Entry(root, width=40)
msg_entry.pack(side=tk.LEFT, padx=5, pady=5)

def send_message(event=None):
    msg = msg_entry.get()
    if msg:
        encrypted = encrypt_message(msg)

        # Show ciphertext
        chat_area.insert(tk.END, f"Ciphertext: {encrypted.hex()}\n", "gray")

        conn.sendall(encrypted)

        chat_area.insert(tk.END, f"You: {msg}\n", "blue")
        chat_area.yview(tk.END)
        msg_entry.delete(0, tk.END)

send_btn = tk.Button(root, text="Send", command=send_message)
send_btn.pack(side=tk.LEFT)

root.bind('<Return>', send_message)

# Networking
s = socket.socket()
s.bind((socket.gethostname(), 5000))
s.listen()

print("Waiting for connection...")
conn, addr = s.accept()
print("Connected to", addr)

def receive_messages():
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            # Show ciphertext
            chat_area.insert(tk.END, f"Ciphertext: {data.hex()}\n", "gray")

            msg = decrypt_message(data)
            chat_area.insert(tk.END, f"Client: {msg}\n", "red")
            chat_area.yview(tk.END)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()

conn.close()
s.close()