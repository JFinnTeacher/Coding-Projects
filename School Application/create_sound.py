import wave
import math
import struct
import os
import sys

try:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set the output path for the WAV file
    output_path = os.path.join(script_dir, 'timer_end.wav')
    
    print(f"Creating sound file at: {output_path}")
    
    # Audio will be mono, 16-bit, 44.1kHz
    sample_rate = 44100
    duration = 0.8  # seconds
    frequency = 880  # Hz (A5 note)
    num_samples = int(duration * sample_rate)

    # Generate sine wave
    samples = []
    for i in range(num_samples):
        # Create a beeping pattern
        if (i // (sample_rate // 5)) % 2 == 0:  # Alternates between sound and silence
            sample = math.sin(2 * math.pi * frequency * i / sample_rate)
            # Convert to 16-bit integer
            sample = int(sample * 32767)
        else:
            sample = 0
        samples.append(sample)

    # Create and write the WAV file
    with wave.open(output_path, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        
        # Write the samples
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

    print(f"Timer sound file created successfully at {output_path}")
    
    # Verify the file was created
    if os.path.exists(output_path):
        print(f"File size: {os.path.getsize(output_path)} bytes")
    else:
        print("Warning: File was not created!")

except Exception as e:
    print(f"Error creating sound file: {str(e)}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    sys.exit(1) 