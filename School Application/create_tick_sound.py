import wave
import math

def create_tick_sound():
    # Audio parameters
    duration = 0.1  # seconds
    sample_rate = 44100  # Hz
    frequency = 1000  # Hz
    amplitude = 0.5
    
    # Calculate number of frames
    num_frames = int(duration * sample_rate)
    
    # Create audio data
    audio_data = []
    for i in range(num_frames):
        t = i / sample_rate
        value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * t))
        # Convert to 2 bytes (16-bit)
        audio_data.append(value.to_bytes(2, byteorder='little', signed=True))
    
    # Create WAV file
    with wave.open('timer_tick.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(audio_data))

if __name__ == '__main__':
    create_tick_sound() 