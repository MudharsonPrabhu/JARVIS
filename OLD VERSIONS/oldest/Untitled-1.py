# Test: Print volume levels to calibrate threshold
import sounddevice as sd
import numpy as np

def print_volume():
    def callback(indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        print("Volume:", volume_norm)
    with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=1024):
        print("Speak or clap to test volume...")
        while True:
            sd.sleep(200)

# Uncomment to run this test
# print_volume()