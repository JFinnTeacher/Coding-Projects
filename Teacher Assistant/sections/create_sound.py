import wave
import struct
import os
from pathlib import Path

def create_beep_sound():
    # Create sounds directory if it doesn't exist
    sound_dir = Path("sounds")
    sound_dir.mkdir(exist_ok=True)
    
    # Sound parameters
    duration = 1.0  # seconds
    frequency = 440.0  # Hz (A4 note)
    sample_rate = 44100  # Hz
    amplitude = 32767  # Max amplitude for 16-bit audio
    
    # Create WAV file
    with wave.open(str(sound_dir / "timer_end.wav"), 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        
        # Generate samples
        for i in range(int(duration * sample_rate)):
            value = int(amplitude * (1 - i / (duration * sample_rate)))  # Fade out
            data = struct.pack('<h', value)
            wav_file.writeframes(data)

if __name__ == "__main__":
    create_beep_sound() 