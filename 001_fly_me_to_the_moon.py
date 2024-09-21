import pygame
import numpy as np
import time

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Define the frequencies of notes (C3 to B4)
NOTES = {
    'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61,
    'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
    'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88
}

def generate_sine_wave(freq, duration, volume=0.5):
    """Generate a C-contiguous stereo sine wave array for a given frequency, duration, and volume."""
    samples = int(44100 * duration)
    t = np.linspace(0, duration, samples, False)
    wave = np.sin(2 * np.pi * freq * t) * volume
    stereo_wave = np.column_stack((wave, wave))  # Create a stereo array
    return (stereo_wave * 32767).astype(np.int16)

def play_note(note, duration):
    """Play a note for a given duration."""
    if note in NOTES:
        frequency = NOTES[note]
        sound_array = generate_sine_wave(frequency, duration)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.play()
        time.sleep(duration)
    else:
        time.sleep(duration)  # Rest for notes not in our frequency dictionary

def play_melody(melody, durations):
    """Play a melody given a list of notes and their durations."""
    for note, duration in zip(melody, durations):
        play_note(note, duration)

# Define the melody and durations
melody = ['C4', 'B3', 'A3', 'G3', 'F3', 
          'A3', 'C4', 'B3', 'A3', 'G3', 'F3', 'E3', 
          'A3', 'G#3', 'F3', 'E3', 'D3', 'C3', 
          'D3', 'D3', 'A3', 'A3', 'C4', 'D4', 'G3', 
          'C3', 'C3', 'G3', 'G3', 'A3', 'G3', 'F3', 'F3']

# Define durations for each note (in seconds)
durations = [0.6, 0.6, 0.6, 0.6, 1.2,
             0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2,
             0.6, 0.6, 0.6, 0.6, 0.6, 1.2,
             0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2,
             0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1.2]

# Play the melody
play_melody(melody, durations)

# Wait for the sound to finish and then quit
pygame.time.wait(1000)
pygame.quit()