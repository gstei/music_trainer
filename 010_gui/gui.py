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
        ttk.Label(mic_frame, text="Input:").pack(side=tk.LEFT)
        self.mic_var = tk.StringVar(master)
        self.mic_var.set("Select Microphone")
        self.mic_var.trace("w", self.update_mic_label)
        self.mic_option = ttk.Combobox(mic_frame, textvariable=self.mic_var, state="readonly")
        self.mic_option.pack(side=tk.LEFT)
        self.mic_label = ttk.Label(mic_frame, text="No microphone selected")
        self.mic_label.pack(side=tk.LEFT, padx=10)

        # Speaker selection
        speaker_frame = ttk.Frame(self.main_frame)
        speaker_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(speaker_frame, text="Output:").pack(side=tk.LEFT)
        self.speaker_var = tk.StringVar(master)
        self.speaker_var.set("Select Speaker")
        self.speaker_option = ttk.Combobox(speaker_frame, textvariable=self.speaker_var, state="readonly")
        self.speaker_option.pack(side=tk.LEFT)

        # Play recording button
        self.play_recording_button = ttk.Button(self.main_frame, text="Play Recording", command=self.play_recording)
        self.play_recording_button.grid(row=6, column=0, sticky=tk.W, pady=5)

        # Latest recording label
        self.recording_label = ttk.Label(self.main_frame, text="No recordings yet")
        self.recording_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Theme switch
        self.theme_switch = ttk.Checkbutton(self.main_frame, text="Dark Mode", style="Switch.TCheckbutton", command=self.toggle_theme)
        self.theme_switch.grid(row=8, column=0, sticky=tk.W, pady=10)

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
        self.is_paused = False
        self.current_pos = 0
        self.end_time = 0
        
        # Create recordings folder if it doesn't exist
        if not os.path.exists(self.recordings_folder):
            os.makedirs(self.recordings_folder)

        # Populate microphone and speaker options
        self.populate_audio_devices()

        # Ensure all widgets use the correct style
        self.setup_ui()

    def create_styles(self):
        # Set up the styles for the GUI elements
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TButton", padding=6, relief="flat", background="#e0e0e0", foreground="black")
        self.style.map("TButton", background=[("active", "#d0d0d0"), ("pressed", "#c0c0c0")])
        self.style.configure("TLabel", background="#f0f0f0", foreground="black")
        self.style.configure("TEntry", fieldbackground="white", foreground="black")
        self.style.configure("TCombobox", fieldbackground="white", background="#e0e0e0", foreground="black")
        self.style.map("TCombobox", fieldbackground=[("readonly", "white")])
        self.style.configure("Switch.TCheckbutton", background="#f0f0f0", foreground="black")
        self.style.map("Switch.TCheckbutton", 
                       background=[("active", "#e0e0e0")],
                       foreground=[("active", "black")])

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            entry_bg = "#3c3c3c"
            button_bg = "#4a4a4a"
            button_fg = "#ffffff"
            button_active = "#606060"
            switch_active_bg = "#3c3c3c"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            entry_bg = "#ffffff"
            button_bg = "#e0e0e0"
            button_fg = "#000000"
            button_active = "#d0d0d0"
            switch_active_bg = "#e0e0e0"

        # Configure styles for ttk widgets
        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TButton", background=button_bg, foreground=button_fg)
        self.style.map("TButton", background=[("active", button_active), ("pressed", button_active)])
        self.style.configure("TLabel", background=bg_color, foreground=fg_color)
        self.style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=button_bg, foreground=fg_color)
        self.style.map("TCombobox", fieldbackground=[("readonly", entry_bg)])
        self.style.configure("Switch.TCheckbutton", background=bg_color, foreground=fg_color)
        self.style.map("Switch.TCheckbutton", 
                    background=[("active", switch_active_bg)],
                    foreground=[("active", fg_color)])

        # Update the main window background
        self.master.configure(bg=bg_color)

        # Update all child widgets
        for widget in self.main_frame.winfo_children():
            widget_type = widget.winfo_class()
            if widget_type in ('TFrame', 'TLabel', 'TButton', 'TEntry', 'TCombobox'):
                widget.configure(style=widget_type)

        # Special handling for Comboboxes
        self.mic_option.configure(style="TCombobox")
        self.speaker_option.configure(style="TCombobox")

        # Update the theme switch text
        self.theme_switch.config(text="Light Mode" if self.dark_mode else "Dark Mode")

        # Force redraw of the main frame
        self.main_frame.update()

    def setup_ui(self):
        # Ensure all buttons use the correct style
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(style="TButton")

    def select_file(self):
        # Open file dialog to select an MP3 file
        self.file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))
            self.playback_position = 0

    def toggle_playback(self):
        if self.is_playing:
            self.pause_audio()
        else:
            self.play_audio()

    def play_audio(self):
        if not self.file_path:
            messagebox.showerror("Error", "No song selected. Please select an MP3 file first.")
            return
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        if not self.is_paused:
            # Starting playback from the beginning or specified start time
            start = float(self.start_time.get())
            stop = self.stop_time.get()
            
            audio = AudioSegment.from_mp3(self.file_path)
            if stop.lower() == 'end':
                self.end_time = len(audio) / 1000  # Convert to seconds
            else:
                self.end_time = float(stop)
            
            segment = audio[int(start*1000):int(self.end_time*1000)]
            
            self.cleanup_temp_file()
            self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            segment.export(self.temp_file.name, format="wav")
            self.temp_file.close()  # Close the file but don't delete it
            
            try:
                pygame.mixer.music.load(self.temp_file.name)
                pygame.mixer.music.play()
                self.current_pos = start
            except pygame.error as e:
                messagebox.showerror("Error", f"Failed to load audio: {str(e)}")
                return
        else:
            # Resuming from paused state
            pygame.mixer.music.unpause()
        
        self.is_playing = True
        self.is_paused = False
        self.play_stop_button.config(text="Stop")
        
        # Start a thread to monitor playback
        threading.Thread(target=self.monitor_playback, daemon=True).start()
        
    def monitor_playback(self):
        while self.is_playing:
            if not pygame.mixer.music.get_busy() and not self.is_paused:
                self.stop_audio()
                self.current_pos = float(self.start_time.get())  # Reset to start time
                break
            elif not self.is_paused:
                self.current_pos = float(self.start_time.get()) + pygame.mixer.music.get_pos() / 1000
                if self.current_pos >= self.end_time:
                    self.stop_audio()
                    self.current_pos = float(self.start_time.get())  # Reset to start time
                    break
            time.sleep(0.1)
        
    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.play_stop_button.config(text="Play")
            self.current_pos += pygame.mixer.music.get_pos() / 1000  # Update current position

    def process_audio(self, start, stop):
        # Process the audio file for playback
        audio = AudioSegment.from_mp3(self.file_path)
        
        if stop.lower() == 'end':
            stop = len(audio) / 1000
        else:
            stop = int(stop)

        segment = audio[start*1000:stop*1000]
        
        self.cleanup_temp_file()
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        segment.export(self.temp_file.name, format="mp3")
        self.temp_file.close()
        
        self.audio_queue.put((self.temp_file.name, start))

    def check_audio_thread(self):
        # Check the status of the audio processing thread
        if self.audio_thread.is_alive():
            self.master.after(100, self.check_audio_thread)
        else:
            if not self.audio_queue.empty():
                temp_file_name, start_time = self.audio_queue.get()
                pygame.mixer.music.load(temp_file_name)
                pygame.mixer.music.play()
                self.current_start_time = start_time
                self.playback_start_time = time.time()
                self.master.after(100, self.check_playback_status)
            else:
                self.playback_finished()

    def check_playback_status(self):
        # Continuously check if the playback has finished
        if pygame.mixer.music.get_busy():
            self.master.after(100, self.check_playback_status)
        else:
            self.playback_finished()

    def playback_finished(self):
        # Handle the end of playback
        self.is_playing = False
        self.play_stop_button.config(text="Play")
        self.playback_position = int(self.start_time.get())

    def stop_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        self.is_playing = False
        self.play_stop_button.config(text="Play")

    def reset_audio(self):
        self.stop_audio()
        self.cleanup_temp_file()
        self.current_pos = float(self.start_time.get())
        self.is_paused = False

    def cleanup_temp_file(self):
        if self.temp_file:
            try:
                pygame.mixer.music.unload()
            except:
                pass
            try:
                os.unlink(self.temp_file.name)
            except:
                pass
            self.temp_file = None

    def toggle_recording(self):
        # Toggle between start and stop recording
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        # Start audio recording
        self.recording = True
        self.record_button.config(text="Stop Recording")
        self.frames = []
        
        def record_thread():
            input_device_index = self.get_device_index(self.mic_var.get())
            stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, 
                                     input=True, input_device_index=input_device_index,
                                     frames_per_buffer=1024)
            while self.recording:
                data = stream.read(1024)
                self.frames.append(data)
            stream.stop_stream()
            stream.close()

        threading.Thread(target=record_thread).start()
        
    def stop_recording(self):
        # Stop audio recording and save the file
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
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            
            # Set the output device for playback
            output_device_index = self.get_device_index(self.speaker_var.get())
            if output_device_index is not None:
                try:
                    pygame.mixer.quit()
                    pygame.mixer.init(devicename=self.speaker_var.get())
                except pygame.error:
                    messagebox.showerror("Error", "Failed to set output device. Using default.")
            
            pygame.mixer.music.load(self.latest_recording)
            pygame.mixer.music.play()
        else:
            messagebox.showinfo("Info", "No recordings available.")

    def populate_audio_devices(self):
        # Populate the microphone and speaker selection dropdowns
        input_devices = []
        output_devices = []
        for i in range(self.audio.get_device_count()):
            dev_info = self.audio.get_device_info_by_index(i)
            if dev_info['maxInputChannels'] > 0:
                input_devices.append(dev_info['name'])
            if dev_info['maxOutputChannels'] > 0:
                output_devices.append(dev_info['name'])
        
        self.mic_option['values'] = ["Select Microphone"] + input_devices
        self.speaker_option['values'] = ["Select Speaker"] + output_devices

    def update_mic_label(self, *args):
        # Update the label showing the selected microphone
        selected_mic = self.mic_var.get()
        if selected_mic != "Select Microphone":
            self.mic_label.config(text=selected_mic)
        else:
            self.mic_label.config(text="No microphone selected")

    def get_device_index(self, device_name):
        # Get the index of a device by its name
        for i in range(self.audio.get_device_count()):
            dev_info = self.audio.get_device_info_by_index(i)
            if dev_info['name'] == device_name:
                return i
        return None

    def __del__(self):
        # Cleanup method called when the object is destroyed
        self.cleanup_temp_file()
        self.audio.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAudioPlayerRecorder(root)
    root.mainloop()