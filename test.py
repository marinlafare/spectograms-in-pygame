import pygame
import numpy as np
import threading
import pyaudio
import scipy
import scipy.fftpack
import scipy.io.wavfile
import sys
import wave

FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100
DEVICE = 1
windowWidth = 500
FFTSIZE = 512

def graphFFT(pcm):
    global data
    ffty = scipy.fftpack.fft(pcm)
    ffty = abs(ffty[0:int(len(ffty)/2)])/200
    
    for i in range(len(ffty)):
        if ffty[i] < 0:
            ffty[i] = 0
        if ffty[i] > 255:
            ffty[i] = 255
    
    data = np.roll(data, -1, 0)
    data[-1] = ffty[::-1]
    
def record():
    p = pyaudio.PyAudio()
    inStream = p.open(format = FORMAT,
                      channels = 1,
                      rate=SAMPLE_RATE,
                      input_device_index=DEVICE,
                      input=True)

    while True:
        pcm = np.frombuffer(
                            inStream.read(FFTSIZE),
                            dtype=np.int16)
        graphFFT(pcm)


pal = [(max((x-128)*2, 0), x, min(x*2, 255)) for x in range(256)]
data = np.array(np.zeros((windowWidth, int(FFTSIZE/2))), dtype=int)

pygame.init() 
pygame.display.set_caption("Simple Spectrograph")
screen = pygame.display.set_mode((windowWidth, FFTSIZE/2))
world = pygame.Surface((windowWidth, FFTSIZE/2), depth=8)  # MAIN SURFACE
world.set_palette(pal)

t_rec = threading.Thread(target=record)
t_rec.daemon = True
t_rec.start()

clk = pygame.time.Clock()
while 1:
    for event in pygame.event.get():  # check if we need to exit
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    pygame.surfarray.blit_array(world, data)  # place data in window
    screen.blit(world, (0, 0))
    pygame.display.flip()  # RENDER WINDOW
    clk.tick(30)  # limit to 30FPS