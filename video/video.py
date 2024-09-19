import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import numpy as np
import random
import string
import threading

class VideoSteganography:

    def __init__(self, root):
        self.root = root
        self.root.title("Video Steganography")
        self.root.geometry("800x450")
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

        self.log = tk.Text(root, width=50, height=2)
        self.log.pack(pady=10)

        # Left side for encoding
        left_frame = tk.Frame(root)
        left_frame.pack(side="left", padx=20)

        ttk.Label(left_frame, text="Select Video to Encode:").pack()
        self.encode_button = ttk.Button(left_frame, text="Add Video", command=self.select_video)
        self.encode_button.pack(pady=10)

        ttk.Label(left_frame, text="Enter the message:").pack()
        self.text_entry = ttk.Entry(left_frame, width=40)
        self.text_entry.pack(pady=10)

        ttk.Label(left_frame, text="Enter the Frame:").pack()
        self.frame_entry = ttk.Entry(left_frame, width=20)
        self.frame_entry.pack(pady=10)

        self.encode_button = ttk.Button(left_frame, text="Perform Steganography", command=self.encode_vid_data)
        self.encode_button.pack(pady=10)

        # Separator
        ttk.Separator(left_frame, orient='vertical').pack(fill='y', padx=10, pady=10, side='right')

        # Right side for decoding
        right_frame = tk.Frame(root)
        right_frame.pack(side="right", padx=20)

        ttk.Label(right_frame, text="Select Encoded Video:").pack()
        self.decode_button = ttk.Button(right_frame, text="Select Video", command=self.select_encoded_image)
        self.decode_button.pack(pady=10)

        ttk.Label(right_frame, text="Select Key:").pack()
        self.key_button = ttk.Button(right_frame, text="Select Key", command=self.select_key)
        self.key_button.pack(pady=10)

        ttk.Label(right_frame, text="Enter the Frame:").pack()
        self.rframe_entry = ttk.Entry(right_frame, width=20)
        self.rframe_entry.pack(pady=10)

        self.get_message_button = ttk.Button(right_frame, text="Get Hidden Message", command=self.decode_vid_data)
        self.get_message_button.pack(pady=10)

        self.message_text = tk.Text(right_frame, height=5, width=40)
        self.message_text.pack(pady=10)

        self.video_path = None
        self.key_path = None
        self.key = None

    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="Select Video to Encode")
        self.log.delete("1.0", tk.END)
        self.log.insert("1.0", "Video Added")

    def generate_key(self):
        # Define the characters you want to include in the random text
        characters = string.ascii_letters + string.digits

        # Use random.choice to select characters randomly and join them into a string
        key = ''.join(random.choice(characters) for _ in range(10))

        return key

    def select_encoded_image(self):
        self.video_path = filedialog.askopenfilename(title="Select Encoded Video")
        self.log.delete("1.0", tk.END)
        self.log.insert("1.0", "Video Added")

    def select_key(self):
        self.key_path = filedialog.askopenfilename(title="Select Key")
        with open(self.key_path, 'r') as key_file:
            self.key = key_file.read()
            self.log.delete("1.0", tk.END)
            self.log.insert("1.0", self.key)

    def msgtobinary(self, msg):
        if type(msg) == str:
            result = ''.join([format(ord(i), "08b") for i in msg])

        elif type(msg) == bytes or type(msg) == np.ndarray:
            result = [format(i, "08b") for i in msg]

        elif type(msg) == int or type(msg) == np.uint8:
            result = format(msg, "08b")

        else:
            raise TypeError("Input type is not supported in this function")

        return result

    def KSA(self, key):
        key_length = len(key)
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % key_length]) % 256
            S[i], S[j] = S[j], S[i]
        return S

    def PRGA(self, S, n):
        i = 0
        j = 0
        key = []
        while n > 0:
            n = n - 1
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            K = S[(S[i] + S[j]) % 256]
            key.append(K)
        return key

    def preparing_key_array(self, s):
        return [ord(c) for c in s]

    def encryption(self, plaintext):
        key = self.generate_key()
        self.key_path = f"{self.video_path}Key.txt"
        with open(self.key_path, 'w') as file:
            file.write(key)
        key = self.preparing_key_array(key)

        S = self.KSA(key)

        keystream = np.array(self.PRGA(S, len(plaintext)))
        plaintext = np.array([ord(i) for i in plaintext])

        cipher = keystream ^ plaintext
        ctext = ''
        for c in cipher:
            ctext = ctext + chr(c)
        return ctext

    def decryption(self, ciphertext):
        print(self.key)
        key = self.key
        key = self.preparing_key_array(key)

        S = self.KSA(key)

        keystream = np.array(self.PRGA(S, len(ciphertext)))
        ciphertext = np.array([ord(i) for i in ciphertext])

        decoded = keystream ^ ciphertext
        dtext = ''
        for c in decoded:
            dtext = dtext + chr(c)
        return dtext

    def embed(self, frame):
        data = self.text_entry.get()
        data = self.encryption(data)
        if (len(data) == 0):
            raise ValueError('Data entered to be encoded is empty')

        data += '*^*^*'

        binary_data = self.msgtobinary(data)
        length_data = len(binary_data)

        index_data = 0

        for i in frame:
            for pixel in i:
                r, g, b = self.msgtobinary(pixel)
                if index_data < length_data:
                    pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data < length_data:
                    pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                    index_data += 1
                if index_data >= length_data:
                    break
        return frame

    def extract(self, frame):
        data_binary = ""
        final_decoded_msg = ""
        for i in frame:
            for pixel in i:
                r, g, b = self.msgtobinary(pixel)
                data_binary += r[-1]
                data_binary += g[-1]
                data_binary += b[-1]
                total_bytes = [data_binary[i: i+8] for i in range(0, len(data_binary), 8)]
                decoded_data = ""
                for byte in total_bytes:
                    decoded_data += chr(int(byte, 2))
                    if decoded_data[-5:] == "*^*^*":
                        for i in range(0, len(decoded_data) - 5):
                            final_decoded_msg += decoded_data[i]
                        final_decoded_msg = self.decryption(final_decoded_msg)
        print("message: ", final_decoded_msg)
        self.message_text.delete(1.0, tk.END)
        self.message_text.insert(tk.END, final_decoded_msg)

    def encode_vid_data(self):
        cap = cv2.VideoCapture(self.video_path)
        vidcap = cv2.VideoCapture(self.video_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_width = int(vidcap.get(3))
        frame_height = int(vidcap.get(4))

        size = (frame_width, frame_height)
        out = cv2.VideoWriter(f'{self.video_path}Steg.mp4', fourcc, 25.0, size)
        max_frame = 0;
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False:
                break
            max_frame += 1
        cap.release()
        self.log.insert("1.0", str(max_frame))
        n = int(self.frame_entry.get())
        frame_number = 0
        while vidcap.isOpened():
            frame_number += 1
            ret, frame = vidcap.read()
            if ret == False:
                break
            if frame_number == n:
                change_frame_with = self.embed(frame)
                frame_ = change_frame_with
                frame = change_frame_with
                self.rem =  frame_
            out.write(frame)
        self.log.delete("1.0", tk.END)
        self.log.insert("1.0", "Encoded the data successfully in the video file.")
        self.video_path = None
        print(frame_)
        return frame_
        

    def decode_vid_data(self):
        if self.video_path and self.key_path:
            # First, find the total number of frames in the video
            cap = cv2.VideoCapture(self.video_path)
            max_frame = 0;
            while cap.isOpened():
                ret, frame = cap.read()
                if ret == False:
                    break
                max_frame += 1
            cap.release()  # Release the first capture object
            n = int(self.rframe_entry.get())
            # Now, use a separate capture object (vidcap) to read frames for decoding
            vidcap = cv2.VideoCapture(self.video_path)
            frame_number = 0
            frame_ = self.rem
            while vidcap.isOpened():
                frame_number += 1
                ret, frame = vidcap.read()
                if ret == False:
                    break
                if frame_number == n:
                    if frame.all() == frame_.all():
                        print("extract")
                        self.extract(frame)
                        return

if __name__ == '__main__':
    root = tk.Tk()
    app = VideoSteganography(root)
    root.mainloop()
