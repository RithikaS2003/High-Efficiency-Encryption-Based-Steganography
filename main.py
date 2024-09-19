import tkinter as tk
from image.image import ImageSteganography
from text.text import TextSteganography
from audio.audio import AudioSteganography
from video.video import VideoSteganography

class MainWindow:

    def __init__(self, root):
        self.root = root
        self.root.title("Steganography")
        self.root.geometry("260x280")
        self.root.resizable(False, False)  # Disable maximize button

        button_style = {
            "width": 20,
            "height": 2,
            "font": ("Helvetica", 14),
            "bg": "violet",
            "fg": "black",
            "relief": "raised",
        }

        text_button = tk.Button(root, text="Text", **button_style, command=self.open_text)
        audio_button = tk.Button(root, text="Audio", **button_style, command=self.open_audio)
        image_button = tk.Button(root, text="Image", **button_style, command=self.open_image)
        video_button = tk.Button(root, text="Video", **button_style, command=self.open_video)

        text_button.pack(pady=5)
        audio_button.pack(pady=5)
        image_button.pack(pady=5)
        video_button.pack(pady=5)

    def open_text(self):
        new = tk.Toplevel()
        instance = TextSteganography(new)
    
    def open_audio(self):
        new = tk.Toplevel()
        instance = AudioSteganography(new)
    
    def open_image(self):
        new = tk.Toplevel()
        instance = ImageSteganography(new)
    
    def open_video(self):
        new = tk.Toplevel()
        instance = VideoSteganography(new)


if __name__ == '__main__':
    root = tk.Tk()
    obj = MainWindow(root)
    root.mainloop()
