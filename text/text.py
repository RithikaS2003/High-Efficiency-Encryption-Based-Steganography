import tkinter as tk
from tkinter import filedialog, ttk
from cryptography.fernet import Fernet
import base64

class TextSteganography:

    def __init__(self, root):
        self.root = root
        self.root.title("Text Steganography")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        # Create a style for buttons
        style = ttk.Style()
        style.configure("TButton", padding=(5, 5), font=("Helvetica", 12))

        # Custom color schemes
        style.map("TButton",
            background=[("active", "dodgerblue"), ("pressed", "cyan")],
            foreground=[("active", "white"), ("pressed", "black")]
        )
        style.configure("TLabel", font=("Helvetica", 14), foreground="blue")

        # Left side for encoding
        left_frame = tk.Frame(root)
        left_frame.pack(side="left", padx=20)

        ttk.Label(left_frame, text="Select Text File to Encode:").pack()
        self.encode_button = ttk.Button(left_frame, text="Add Text File", command=self.select_text_file)
        self.encode_button.pack(pady=10)

        ttk.Label(left_frame, text="Enter the message:").pack()
        self.text_entry = ttk.Entry(left_frame, width=40)
        self.text_entry.pack(pady=10)

        self.encode_button = ttk.Button(left_frame, text="Perform Text Steganography", command=self.encode_text)
        self.encode_button.pack(pady=10)

        self.save_button = ttk.Button(left_frame, text="Save Text and Key", command=self.save_text_and_key)
        self.save_button.pack(pady=10)

        # Separator
        ttk.Separator(left_frame, orient='vertical').pack(fill='y', padx=10, pady=10, side='right')

        # Right side for decoding
        right_frame = tk.Frame(root)
        right_frame.pack(side="right", padx=20)

        ttk.Label(right_frame, text="Select Encoded Text File:").pack()
        self.decode_button = ttk.Button(right_frame, text="Select Text File", command=self.select_encoded_text_file)
        self.decode_button.pack(pady=10)

        ttk.Label(right_frame, text="Select Key:").pack()
        self.key_button = ttk.Button(right_frame, text="Select Key", command=self.select_key)
        self.key_button.pack(pady=10)

        self.get_message_button = ttk.Button(right_frame, text="Get Hidden Message", command=self.get_hidden_message)
        self.get_message_button.pack(pady=10)

        self.message_text = tk.Text(right_frame, height=5, width=40)
        self.message_text.pack(pady=10)

        self.text_file_path = None
        self.key_path = None

    def select_text_file(self):
        self.text_file_path = filedialog.askopenfilename(title="Select Text File to Encode")

    def encode_text(self):
        if self.text_file_path:
            text = self.text_entry.get()
            if text:
                # Encrypt the message with a secret key
                key = Fernet.generate_key()
                cipher_suite = Fernet(key)
                encrypted_message = cipher_suite.encrypt(text.encode())

                # Encode the encrypted message in base64 and append it to the original text
                with open(self.text_file_path, 'a') as file:
                    file.write('\n')
                    file.write(base64.b64encode(encrypted_message).decode())
                
                self.key_path = self.text_file_path.replace('.txt', 'key.key')
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
                self.text_entry.delete(0, 'end')
                self.text_entry.insert(0, "Text encrypted and hidden in the original file.")
            else:
                self.text_entry.delete(0, 'end')
                self.text_entry.insert(0, "Please enter a message.")

    def save_text_and_key(self):
        if self.text_file_path and self.key_path:
            original_text_file_path = self.text_file_path
            new_key_path = original_text_file_path.replace('.txt', 'key.key')
            with open(self.key_path, 'rb') as key_file:
                key_content = key_file.read()
            with open(new_key_path, 'wb') as new_key_file:
                new_key_file.write(key_content)
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, f"Key saved as {new_key_path}.")
        else:
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, "Key not available for saving.")

    def select_encoded_text_file(self):
        self.text_file_path = filedialog.askopenfilename(title="Select Encoded Text File")

    def select_key(self):
        self.key_path = filedialog.askopenfilename(title="Select Key")

    def get_hidden_message(self):
        if self.text_file_path and self.key_path:
            with open(self.text_file_path, 'r') as file:
                lines = file.readlines()
                if len(lines) > 0:
                    encoded_message = base64.b64decode(lines[-1].strip())
                    # Decrypt the message using the provided key
                    with open(self.key_path, 'rb') as key_file:
                        key = key_file.read()
                    cipher_suite = Fernet(key)
                    decrypted_message = cipher_suite.decrypt(encoded_message)
                    self.message_text.delete('1.0', tk.END)
                    self.message_text.insert(tk.END, decrypted_message.decode())
                else:
                    self.message_text.delete('1.0', tk.END)
                    self.message_text.insert(tk.END, "No hidden message found in the file.")
        else:
            self.message_text.delete('1.0', tk.END)
            self.message_text.insert(tk.END, "Text or Key not available for decoding.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextSteganography(root)
    root.mainloop()
