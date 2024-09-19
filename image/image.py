import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet

class ImageSteganography:

    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography")
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

        ttk.Label(left_frame, text="Select Image to Encode:").pack()
        self.encode_button = ttk.Button(left_frame, text="Add Image", command=self.select_image)
        self.encode_button.pack(pady=10)

        ttk.Label(left_frame, text="Enter the message:").pack()
        self.text_entry = ttk.Entry(left_frame, width=40)
        self.text_entry.pack(pady=10)

        self.encode_button = ttk.Button(left_frame, text="Perform Steganography", command=self.encode_image)
        self.encode_button.pack(pady=10)

        self.save_button = ttk.Button(left_frame, text="Save Image and Key", command=self.save_image_and_key)
        self.save_button.pack(pady=10)

        # Separator
        ttk.Separator(left_frame, orient='vertical').pack(fill='y', padx=10, pady=10, side='right')

        # Right side for decoding
        right_frame = tk.Frame(root)
        right_frame.pack(side="right", padx=20)

        ttk.Label(right_frame, text="Select Encoded Image:").pack()
        self.decode_button = ttk.Button(right_frame, text="Select Image", command=self.select_encoded_image)
        self.decode_button.pack(pady=10)

        ttk.Label(right_frame, text="Select Key:").pack()
        self.key_button = ttk.Button(right_frame, text="Select Key", command=self.select_key)
        self.key_button.pack(pady=10)

        self.get_message_button = ttk.Button(right_frame, text="Get Hidden Message", command=self.get_hidden_message)
        self.get_message_button.pack(pady=10)

        self.message_text = tk.Text(right_frame, height=5, width=40)
        self.message_text.pack(pady=10)

        self.image_path = None
        self.key_path = None

    def select_image(self):
        self.image_path = filedialog.askopenfilename(title="Select Image to Encode")

    def encode_image(self):
        if self.image_path:
            text = self.text_entry.get()
            if text:
                # Encrypt the message with a secret key
                key = Fernet.generate_key()
                cipher_suite = Fernet(key)
                encrypted_message = cipher_suite.encrypt(text.encode())

                image = Image.open(self.image_path)
                encoded_image = self.encode_message_in_image(image, encrypted_message)
                encoded_image_path = self.image_path.replace('.png', 'Steg.png')
                encoded_image.save(encoded_image_path)
                self.image_path = encoded_image_path
                self.key_path = self.image_path.replace('.png', 'key.key')
                with open(self.key_path, 'wb') as key_file:
                    key_file.write(key)
                self.text_entry.delete(0, 'end')
                self.text_entry.insert(0, "Message encrypted and saved.")
            else:
                self.text_entry.delete(0, 'end')
                self.text_entry.insert(0, "Please enter a message.")

    def save_image_and_key(self):
        if self.image_path and self.key_path:
            original_image_path = self.image_path.replace('Steg.png', '.png')
            new_image_path = original_image_path.replace('.png', 'Steg.png')
            new_key_path = original_image_path.replace('.png', 'key.key')
            Image.open(self.image_path).save(new_image_path)
            with open(self.key_path, 'rb') as key_file:
                key_content = key_file.read()
            with open(new_key_path, 'wb') as new_key_file:
                new_key_file.write(key_content)
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, f"Image and Key saved as {new_image_path} and {new_key_path}.")
        else:
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, "Image or Key not available for saving.")

    def select_encoded_image(self):
        self.image_path = filedialog.askopenfilename(title="Select Encoded Image")

    def select_key(self):
        self.key_path = filedialog.askopenfilename(title="Select Key")

    def get_hidden_message(self):
        if self.image_path and self.key_path:
            image = Image.open(self.image_path)
            encrypted_message = self.decode_message_from_image(image)
            if encrypted_message:
                # Decrypt the message using the provided key
                with open(self.key_path, 'rb') as key_file:
                    key = key_file.read()
                cipher_suite = Fernet(key)
                decrypted_message = cipher_suite.decrypt(encrypted_message)
                self.message_text.delete('1.0', tk.END)
                self.message_text.insert(tk.END, decrypted_message.decode())
            else:
                self.message_text.delete('1.0', tk.END)
                self.message_text.insert(tk.END, "Decoding failed.")
        else:
            self.message_text.delete('1.0', tk.END)
            self.message_text.insert(tk.END, "Image or Key not available for decoding.")

    @staticmethod
    def encode_message_in_image(image, message):
        width, height = image.size
        encoded_image = image.copy()
        draw = ImageDraw.Draw(encoded_image)
        font = ImageFont.load_default()

        # Encode each character in the message
        x, y = 10, 10
        for byte in message:
            binary_byte = format(byte, '08b')
            for bit in binary_byte:
                pixel = list(encoded_image.getpixel((x, y)))
                pixel[-1] = int(bit)
                encoded_image.putpixel((x, y), tuple(pixel))
                x += 1
                if x >= width:
                    x = 10
                    y += 1
                    if y >= height:
                        break
        return encoded_image

    @staticmethod
    def decode_message_from_image(image):
        binary_message = bytearray()
        width, height = image.size
        x, y = 10, 10
        byte_buffer = ''
        while y < height:
            pixel = image.getpixel((x, y))
            byte_buffer += str(pixel[-1])
            if len(byte_buffer) == 8:
                binary_message.append(int(byte_buffer, 2))
                byte_buffer = ''
            x += 1
            if x >= width:
                x = 10
                y += 1
                if y >= height:
                    break
        return bytes(binary_message)

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ImageSteganography(root)
#     root.mainloop()
