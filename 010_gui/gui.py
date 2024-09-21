import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import pyaudio
import wave
from pydub import AudioSegment
import threading
import os
import tempfile
import queue
import time
from datetime import datetime

class ModernAudioPlayerRecorder:
    def __init__(self, master):
        self.master = master
        master.title("Modern Audio Player and Recorder")
        
        # Set up styles
        self.style = ttk.Style()
        self.dark_mode = False
        self.create_styles()

        # Main frame
        self.main_frame = ttk.Frame(master, padding="20 20 20 20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Initialize pygame mixer
        pygame.mixer.init()

        # File selection
        self.file_button = ttk.Button(self.main_frame, text="Select MP3 File", command=self.select_file)
        self.file_button.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_label = ttk.Label(self.main_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Start and stop time entry
        time_frame = ttk.Frame(self.main_frame)
        time_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(time_frame, text="Start Time (seconds):").pack(side=tk.LEFT)
        self.start_time = ttk.Entry(time_frame, width=10)
        self.start_time.insert(0, "0")
        self.start_time.pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text="Stop Time (seconds or 'End'):").pack(side=tk.LEFT)
        self.stop_time = ttk.Entry(time_frame, width=10)
        self.stop_time.insert(0, "End")
        self.stop_time.pack(side=tk.LEFT, padx=5)

        # Playback control buttons
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.play_stop_button = ttk.Button(control_frame, text="Play", command=self.toggle_playback)
        self.play_stop_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset_audio)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # Record button
        self.record_button = ttk.Button(self.main_frame, text="Record", command=self.toggle_recording)
        self.record_button.grid(row=3, column=0, sticky=tk.W, pady=5)

        # Microphone selection
        mic_frame = ttk.Frame(self.main_frame)
        mic_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.mic_var = tk.StringVar(master)
        self.mic_var.set("Select Microphone")
        self.mic_var.trace("w", self.update_mic_label)
        self.mic_option = ttk.Combobox(mic_frame, textvariable=self.mic_var, state="readonly")
        self.mic_option.pack(side=tk.LEFT)
        self.mic_label = ttk.Label(mic_frame, text="No microphone selected")
        self.mic_label.pack(side=tk.LEFT, padx=10)

        # Play recording button
        self.play_recording_button = ttk.Button(self.main_frame, text="Play Recording", command=self.play_recording)
        self.play_recording_button.grid(row=5, column=0, sticky=tk.W, pady=5)

        # Latest recording label
        self.recording_label = ttk.Label(self.main_frame, text="No recordings yet")
        self.recording_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Theme switch
        self.theme_switch = ttk.Checkbutton(self.main_frame, text="Dark Mode", style="Switch.TCheckbutton", command=self.toggle_theme)
        self.theme_switch.grid(row=7, column=0, sticky=tk.W, pady=10)

        # Initialize variables
        self.file_path = None
        self.recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.latest_recording = None
        self.current_start_time = 0
        self.temp_file = None
        self.audio_thread = None
        self.audio_queue = queue.Queue()
        self.playback_position = 0
        self.playback_start_time = 0
        self.recordings_folder = "recordings"
        self.is_playing = False
        
        # Create recordings folder if it doesn't exist
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

        # Populate microphone options
        self.populate_mic_options()

        # Ensure all widgets use the correct style
        self.setup_ui()

    def create_styles(self):
        self.style.theme_use('clam')  # Use 'clam' theme as base
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, relief="flat", background="#e0e0e0", foreground="black")
        self.style.map("TButton", background=[("active", "#d0d0d0"), ("pressed", "#c0c0c0")])
        self.style.configure("TLabel", background="#f0f0f0", foreground="black")
        self.style.configure("TEntry", fieldbackground="white", foreground="black")
        self.style.configure("TCombobox", fieldbackground="white", background="#e0e0e0", foreground="black")
        self.style.map("TCombobox", fieldbackground=[("readonly", "white")])
        self.style.configure("Switch.TCheckbutton", background="#f0f0f0", foreground="black")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            # Dark mode
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            entry_bg = "#3c3c3c"
            button_bg = "#4a4a4a"
            button_fg = "#ffffff"
            button_active = "#606060"
        else:
            # Light mode
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            entry_bg = "#ffffff"
            button_bg = "#e0e0e0"
            button_fg = "#000000"
            button_active = "#d0d0d0"

        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TButton", background=button_bg, foreground=button_fg)
        self.style.map("TButton", background=[("active", button_active), ("pressed", button_active)])
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=button_bg, foreground=fg_color)
        self.style.map("TCombobox", fieldbackground=[("readonly", entry_bg)])
        self.style.configure("Switch.TCheckbutton", background=bg_color, foreground=fg_color)

        self.master.configure(background=bg_color)
        self.main_frame.configure(background=bg_color)

        # Update existing widgets
        for widget in self.main_frame.winfo_children():
            widget_type = widget.winfo_class()
            if widget_type == 'TButton':
                widget.configure(style="TButton")
            elif widget_type in ('TLabel', 'TEntry', 'TCombobox'):
                widget.configure(style=widget_type)

        # Special handling for the Combobox
        self.mic_option.configure(style="TCombobox")
        self.mic_option['state'] = 'readonly'  # This triggers a redraw of the Combobox

        # Update the theme switch text
        self.theme_switch.config(text="Light Mode" if self.dark_mode else "Dark Mode")

    def setup_ui(self):
        # Ensure all buttons use the TButton style
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(style="TButton")

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))
            self.playback_position = 0

    def toggle_playback(self):
        if self.is_playing:
            self.stop_audio()
        else:
            self.play_audio()

    def play_audio(self):
        if not self.file_path:
            messagebox.showerror("Error", "No song selected. Please select an MP3 file first.")
            return
        
        start = int(self.start_time.get()) + self.playback_position
        stop = self.stop_time.get()
        
        self.audio_thread = threading.Thread(target=self.process_audio, args=(start, stop))
        self.audio_thread.start()
        
        self.master.after(100, self.check_audio_thread)
        self.is_playing = True
        self.play_stop_button.config(text="Stop")

    def process_audio(self, start, stop):
        audio = AudioSegment.from_mp3(self.file_path)
        
        if stop.lower() == 'end':
            stop = len(audio) / 1000  # Convert to seconds
        else:
            stop = int(stop)

        segment = audio[start*1000:stop*1000]
        
        # Create a new temporary file
        self.cleanup_temp_file()
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        segment.export(self.temp_file.name, format="mp3")
        self.temp_file.close()  # Close the file but don't delete it yet
        
        self.audio_queue.put((self.temp_file.name, start))

    def check_audio_thread(self):
        if self.audio_thread.is_alive():
            self.master.after(100, self.check_audio_thread)
        else:
            if not self.audio_queue.empty():
                temp_file_name, start_time = self.audio_queue.get()
                pygame.mixer.music.load(temp_file_name)
                pygame.mixer.music.play()
                self.current_start_time = start_time
                self.playback_start_time = time.time()
            else:
                # Playback has finished
                self.is_playing = False
                self.play_stop_button.config(text="Play")

    def stop_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            current_time = time.time()
            self.playback_position += int(current_time - self.playback_start_time)
        self.is_playing = False
        self.play_stop_button.config(text="Play")

    def reset_audio(self):
        self.stop_audio()
        self.cleanup_temp_file()
        self.current_start_time = int(self.start_time.get())
        self.playback_position = 0
        self.play_stop_button.config(text="Play")

    def cleanup_temp_file(self):
        if self.temp_file:
            pygame.mixer.music.unload()
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
            self.temp_file = None

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.config(text="Stop Recording")
        self.frames = []
        
        def record_thread():
            stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
            while self.recording:
                data = stream.read(1024)
                self.frames.append(data)
            stream.stop_stream()
            stream.close()

        threading.Thread(target=record_thread).start()

    def stop_recording(self):
        self.recording = False
        self.record_button.config(text="Record")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(self.recordings_folder, filename)
        
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        self.latest_recording = filepath
        self.recording_label.config(text=f"Latest recording: {filename}")

    def play_recording(self):
        if self.latest_recording:
            pygame.mixer.music.load(self.latest_recording)
            pygame.mixer.music.play()
        else:
            messagebox.showinfo("Info", "No recordings available.")

    def populate_mic_options(self):
        mic_list = ["Select Microphone"]
        for i in range(self.audio.get_device_count()):
            dev_info = self.audio.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                mic_list.append(dev_info['name'])
        
        self.mic_option['values'] = mic_list

    def update_mic_label(self, *args):
        selected_mic = self.mic_var.get()
        if selected_mic != "Select Microphone":
            self.mic_label.config(text=selected_mic)
        else:
            self.mic_label.config(text="No microphone selected")

    def __del__(self):
        self.cleanup_temp_file()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAudioPlayerRecorder(root)
    root.mainloop()