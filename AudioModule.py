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
SAMPLEFREQUENCY = 44100        
SAMPLEWIDTH = pyaudio.get_sample_size(pyaudio.paInt16)
latest_samples = []
class Recorder:
    def __init__(self):
        self.recording = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()
        self.latest_samples_object = []
        self.dummy_dummy = [0,1,2,3]

    def record(self):
        print("Recording...")
        stream = self.p.open(format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True)
        frames = []  # Initialize array to store frames
        self.dummy_dummy = [7,8,9]
        self.recording = True
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)
        print("done recording")
        # Stop and close the stream
        latest_samples = frames
        self.latest_samples_object = frames
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        self.p.terminate()
        
    def stop(self):
        print("stop")
        self.recording = False

    def getFrames(self):
        return self.latest_samples_object

"""
Helper class for recording Audio. 
Stores recorded Audio in standard temp file
Filename can be retrieved with get_filename()

Example code on how to use it:

"""

def process_audio(data):
        print("Processing")
        # Save the recorded data as a WAV file
        wf = wave.open(FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        p = pyaudio.PyAudio()
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(SAMPLEFREQUENCY)
        wf.writeframes(b''.join(data))
        wf.close()
        print('Done processing')

        
class Player:
    def __init__(self):
        pass
        
    def play(self, filename): 
        print("Playing the audio ")
        # Open the sound file 
        wf = wave.open(filename, 'rb')

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
        stop_playing = False
        # Play the sound by writing the audio data to the stream
        while data != '' or self.stop_playing:
            stream.write(data)
            data = wf.readframes(CHUNK)
        print('done playing audio')
        # Close and terminate the stream
        stream.close()
        p.terminate()

    def stop_playing():
        self.stop_playing = True


class AudioHelper:
    def __init__(self):
        
        self.player = Player()
                
        t0_p = {'source': 'initial', 'target': 'ready'}
        t1_p = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
        t2_p = {'trigger': 'done', 'source': 'playing', 'target': 'ready'}
        t3_p = {'trigger' : 'stop', 'source' : 'playing', 'target' : 'ready', 'effect' : 'stop_playing'}
        
        s_ready = {'name': 'ready'}
        s_playing = {'name': 'playing', 'do': 'play(*)'}

        self.stm_player = Machine(name='stm_player', transitions=[t0_p, t1_p, t2_p], states=[s_playing, s_ready], obj=self.player)
        self.player.stm = self.stm_player


        self.recorder = Recorder()
                
        t0_r = {'source': 'initial', 'target': 'ready'}
        t1_r = {'trigger': 'start_recording', 'source': 'ready', 'target': 'recording'}
        t2_r = {'trigger': 'stop_recording', 'source': 'recording', 'target': 'stopped_recording', 'effect': 'stop()'}
        t3_r = {'trigger' : 'done', 'source' : 'stopped_recording', 'target' : 'ready'}
        s_ready = {'name': 'ready'}
        s_recording = {'name': 'recording', 'do': 'record()'}
        s_stopped_recording = {'name': 'stopped_recording'}
        self.stm_recording = Machine(name='stm_recording', transitions=[t0_r, t1_r, t2_r, t3_r], states=[s_ready, s_recording, s_stopped_recording], obj=self.recorder)
        self.recorder.stm = self.stm_recording
        self.driver = Driver()
        self.driver.add_machine(self.stm_recording)
        self.driver.add_machine(self.stm_player)
        print('Driver created')
        self.driver.start()

        self.last_record = []
    
    def play_audio(self, filename):
        print("driver started")
        self.stm_player.send('start', args = [filename])
        print("sent start audio signal playing")

    def stop_audio(self):
        self.stm_player.send('stop')

    
    def start_recording(self):
        print("driver started")
        self.driver.send('start_recording', 'stm_recording')
        
    def stop_recording(self):
        self.driver.send('stop_recording', 'stm_recording')

    def get_filename(self):
        #Returns the filename that is used for temp storage
        return FILENAME

    def get_recorded_samples(self):
        stms = []
        #wtf
        for stm_id in self.driver._stms_by_id:
            stms.append(self.driver._stms_by_id[stm_id])
        #return stms[0]._obj.getFrames()
        return []