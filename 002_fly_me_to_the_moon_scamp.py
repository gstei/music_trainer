from scamp import *
import os

# Create a session
s = Session()

# Add an instrument (piano)
piano = s.new_part("piano")

# Define the notes (in MIDI numbers) and durations
melody = [60, 59, 57, 55, 53,  # C4, B3, A3, G3, F3
          57, 60, 59, 57, 55, 53, 52,  # A3, C4, B3, A3, G3, F3, E3
          57, 56, 53, 52, 50, 52, 53,  # A3, G#3, F3, E3, D3, E3, F3
          57, 56, 53, 52, 50, 48,  # A3, G#3, F3, E3, D3, C3
          50, 50, 57, 57, 60, 62, 55,  # D3, D3, A3, A3, C4, D4, G3
          48, 48, 55, 55, 57, 55, 53, 53]  # C3, C3, G3, G3, A3, G3, F3, F3

durations = [1, 1, 1, 1, 2,
             1, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 1, 1, 2,
             1, 1, 1, 1, 1, 2,
             0.5, 0.5, 0.5, 2, 1, 1, 2,
             0.5, 0.5, 0.5, 2, 1, 1, 1, 2]

# Set the tempo (beats per minute)
s.tempo = 90

# Play the melody
s.start_transcribing()
s.wait(1)
for note, duration in zip(melody, durations):
    piano.play_note(note, 0.8, duration, blocking=False)
    s.wait(duration)

performance = s.stop_transcribing()

# Convert the performance to a score
score = performance.to_score()

# Export as PDF
pdf_path = os.path.expanduser("Descargas/fly_me_to_the_moon.pdf")
score.export_pdf(pdf_path)
print(f"PDF score saved to: {pdf_path}")

# Optionally, display the score (if MuseScore is installed)
score.show()

# Export as MusicXML (can be opened in various notation software)
xml_path = os.path.expanduser("Descargas/fly_me_to_the_moon.musicxml")
score.export_music_xml(xml_path)
print(f"MusicXML score saved to: {xml_path}")