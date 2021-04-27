from stmpy import Machine, Driver
from os import system
import os
import time

import pyaudio
import wave

#standard values
FILENAME = "output_tmp.wav"
CHANNELS = 2
SAMPLEFORMAT = pyaudio.paInt16
CHUNK = 1024
SMAPLEFREQUENCY = 44100        
SAMPLEWIDTH = pyaudio.get_sample_size(pyaudio.paInt16)

class Recorder:
    def __init__(self):
        self.recording = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()

    def record(self):
        stream = self.p.open(format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True)
        self.frames = []  # Initialize array to store frames
        # Store data in chunks for 3 seconds
        self.recording = True
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
        print("done recording")
        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        self.p.terminate()
        
    def stop(self):
        print("stop")
        self.recording = False
    
    def process(self):
        print("processing")
        # Save the recorded data as a WAV file
        wf = wave.open(FILENAME, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        print('Done processing')

    def getFrames(self):
        return self.frames

"""
Helper class for recording Audio. 
Stores recorded Audio in standard temp file
Filename can be retrieved with get_filename()

Example code on how to use it:
"
import Audio_Module
import time

helper = Audio_Module.Recording_Helper()
helper.start_recording()
time.sleep(2)
helper.stop_recording()
data = helper.get_record()
"

"""

class Recording_Helper:
    def __init__(self):
        self.recorder = Recorder()
                
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start_recording', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'stop_recording', 'source': 'recording', 'target': 'processing'}

        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()"}
        s_processing = {'name': 'processing', 'do': 'process()'}

        self.stm_recording = Machine(name='stm_recording', transitions=[t0, t1, t2], states=[s_recording, s_processing], obj=self.recorder)
        self.recorder.stm = self.stm_recording
        self.driver = Driver()
        self.driver.add_machine(self.stm_recording)
        print('Driver created')

    def start_recording(self):
        self.driver.start()
        print("driver started")
        self.driver.send('start_recording', 'stm_recording')
        
    def stop_recording(self):
        self.driver.send('stop_recording', 'stm_recording')
        self.driver.stop()

    def get_filename(self):
        #Returns the filename that is used for temp storage
        return FILENAME

    def get_recorded_samples(self):
        return self.recorder.getFrames()


def process(data):
        print("processing")
        # Save the recorded data as a WAV file
        wf = wave.open(FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLEWIDTH)
        wf.setframerate(SMAPLEFREQUENCY)
        wf.writeframes(b''.join(data))
        wf.close()
        print('Done processing')

        
class Player:
    def __init__(self):
        pass
        
    def play(self): 

        # Open the sound file 
        wf = wave.open(FILENAME, 'rb')

        # Create an interface to PortAudio
        p = pyaudio.PyAudio()

        # Open a .Stream object to write the WAV file to
        # 'output = True' indicates that the sound will be played rather than recorded
        stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        # Read data in chunks
        data = wf.readframes(CHUNK)

        # Play the sound by writing the audio data to the stream
        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)

        # Close and terminate the stream
        stream.close()
        p.terminate()






class PlayAudio_Helper:
    def __init__(self):
        
        self.player = Player()
                
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}

        s_playing = {'name': 'playing', 'do': 'play()'}

        self.stm_player = Machine(name='stm_player', transitions=[t0, t1], states=[s_playing], obj=self.player)
        self.player.stm = self.stm_player

        self.driver = Driver()
        self.driver.add_machine(self.stm_player)
    
    def play(self):
        
        self.driver.start()

        print("driver started")

        self.driver.send('start', 'stm_player')
        self.driver.stop()