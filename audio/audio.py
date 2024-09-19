import tkinter as tk
from tkinter import filedialog, ttk
import wave
import array
from cryptography.fernet import Fernet
from pydub import AudioSegment

class AudioSteganography:

    def __init__(self, root):
        self.root = root
        self.root.title("Audio Steganography")
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

        ttk.Label(left_frame, text="Select Audio File to Encode:").pack()
        self.encode_button = ttk.Button(left_frame, text="Add Audio File", command=self.select_audio_file)
        self.encode_button.pack(pady=10)

        ttk.Label(left_frame, text="Enter the message:").pack()
        self.text_entry = ttk.Entry(left_frame, width=40)
        self.text_entry.pack(pady=10)

        self.perform_encode_button = ttk.Button(left_frame, text="Perform Audio Steganography", command=self.encode_audio)
        self.perform_encode_button.pack(pady=10)

        self.save_button = ttk.Button(left_frame, text="Save Audio and Key", command=self.save_audio_and_key)
        self.save_button.pack(pady=10)

        # Separator
        ttk.Separator(left_frame, orient='vertical').pack(fill='y', padx=10, pady=10, side='right')

        # Right side for decoding
        right_frame = tk.Frame(root)
        right_frame.pack(side="right", padx=20)

        ttk.Label(right_frame, text="Select Encoded Audio File:").pack()
        self.decode_button = ttk.Button(right_frame, text="Select Audio File", command=self.select_encoded_audio_file)
        self.decode_button.pack(pady=10)

        ttk.Label(right_frame, text="Select Key:").pack()
        self.key_button = ttk.Button(right_frame, text="Select Key", command=self.select_key)
        self.key_button.pack(pady=10)

        self.get_message_button = ttk.Button(right_frame, text="Get Hidden Message", command=self.get_hidden_message)
        self.get_message_button.pack(pady=10)

        self.message_text = tk.Text(right_frame, height=5, width=40)
        self.message_text.pack(pady=10)

        self.audio_file_path = None
        self.key_path = None

    def select_audio_file(self):
        self.audio_path = filedialog.askopenfilename(title="Select Audio File to Encode")

        if self.audio_path:
            if self.audio_path.endswith(".mp3"):
                # Convert MP3 to WAV
                audio = AudioSegment.from_mp3(self.audio_path)
                wav_path = self.audio_path.replace('.mp3', '.wav')
                audio.export(wav_path, format="wav")
                self.audio_path = wav_path
            self.audio_file_path = self.audio_path

    def encode_audio(self):
        if self.audio_path:
            text = self.text_entry.get()
            if text:
                key = Fernet.generate_key()
                cipher_suite = Fernet(key)
                encrypted_message = cipher_suite.encrypt(text.encode())

                # Save the key to a file with the same base name as the output audio file
                key_path = self.audio_file_path.replace('.wav', 'key.key')
                with open(key_path, 'wb') as key_file:
                    key_file.write(key)

                with wave.open(self.audio_file_path, 'rb') as audio_file:
                    frame_bytes = bytearray(list(audio_file.readframes(audio_file.getnframes())))
                    # Convert '#' to bytes before concatenating
                    padding = int((len(frame_bytes) - (len(encrypted_message) * 8 * 8)) / 8) * b'#'
                    encrypted_message += padding
                    bits = list(map(int, ''.join([bin(i).lstrip('0b').rjust(8, '0') for i in encrypted_message])))
                    for i, bit in enumerate(bits):
                        frame_bytes[i] = (frame_bytes[i] & 254) | bit
                    frame_modified = bytes(frame_bytes)
                    output = self.audio_file_path.replace('.wav', 'Steg.wav')
                    with wave.open(output, 'wb') as fd:
                        fd.setparams(audio_file.getparams())
                        fd.writeframes(frame_modified)

            else:
                self.text_entry.delete(0, 'end')
                self.text_entry.insert(0, "Please enter a message.")
    def save_audio_and_key(self):
        if self.audio_file_path and self.key_path:
            original_audio_path = self.audio_file_path.replace('Steg.wav', '.wav')
            new_audio_path = original_audio_path.replace('.wav', 'Steg.wav')
            new_key_path = original_audio_path.replace('.wav', 'key.key')
            with wave.open(self.audio_file_path, 'rb') as audio_file:
                audio_params = audio_file.getparams()
            with wave.open(new_audio_path, 'wb') as new_audio_file:
                new_audio_file.setparams(audio_params)
                new_audio_file.writeframes(array.array('h', array.array('h', audio_params.nchannels * [0])))
            with open(self.key_path, 'rb') as key_file:
                key_content = key_file.read()
            with open(new_key_path, 'wb') as new_key_file:
                new_key_file.write(key_content)
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, f"Audio and Key saved as {new_audio_path} and {new_key_path}.")
        else:
            self.text_entry.delete(0, 'end')
            self.text_entry.insert(0, "Audio or Key not available for saving.")

    def select_encoded_audio_file(self):
        self.audio_file_path = filedialog.askopenfilename(title="Select Encoded Audio File")

    def select_key(self):
        self.key_path = filedialog.askopenfilename(title="Select Key")

    def get_hidden_message(self):
        if self.audio_file_path and self.key_path:
            encrypted_message = self.decode_message_from_audio(self.audio_file_path)
            if encrypted_message:
                # Decrypt the message using the provided key
                with open(self.key_path, 'rb') as key_file:
                    key = key_file.read()
                cipher_suite = Fernet(key)
                decrypted_message = cipher_suite.decrypt(encrypted_message.encode())
                self.message_text.delete('1.0', tk.END)
                self.message_text.insert(tk.END, decrypted_message.decode())
            else:
                self.message_text.delete('1.0', tk.END)
                self.message_text.insert(tk.END, "Decoding failed.")
        else:
            self.message_text.delete('1.0', tk.END)
            self.message_text.insert(tk.END, "Audio or Key not available for decoding.")

    @staticmethod
    def decode_message_from_audio(audio_path):
        waveaudio = wave.open(audio_path, mode='rb')
        frame_bytes = bytearray(list(waveaudio.readframes(waveaudio.getnframes())))
        extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
        string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
        msg = string.split("###")[0]
        waveaudio.close()
        return msg

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioSteganography(root)
    root.mainloop()
