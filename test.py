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
SAMPLE_RATE = 44100  # try 5000 for HD data, 48000 for realtime
DEVICE = 1
windowWidth = 500
fftsize = 512

def graphFFT(pcm):
    global data
    ffty = scipy.fftpack.fft(pcm)  # convert WAV to FFT
    ffty = abs(ffty[0:int(len(ffty)/2)])/500  # FFT is mirror-imaged
    # ffty=(scipy.log(ffty))*30-50 # if you want uniform data
    #print("MIN:t%stMAX:t%s" % (min(ffty), max(ffty)))
    for i in range(len(ffty)):
        if ffty[i] < 0:
            ffty[i] = 0
        if ffty[i] > 255:
            ffty[i] = 255
    
    data = numpy.roll(data, -1, 0)
    data[-1] = ffty[::-1]
    
def record():
    p = pyaudio.PyAudio()
    inStream = p.open(format = FORMAT,
                      channels = 1,
                      rate=SAMPLE_RATE,
                      input_device_index=DEVICE,
                      input=True)

    linear = [0]*fftsize
    while True:
        linear = linear[int(fftsize):]
        pcm = numpy.frombuffer(inStream.read(
            int(fftsize)), dtype=numpy.int16)
        linear = numpy.append(linear, pcm)
        graphFFT(linear)


pal = [(max((x-128)*2, 0), x, min(x*2, 255)) for x in range(256)]
print( max(pal), min(pal))
data = numpy.array(numpy.zeros((windowWidth, int(fftsize/2))), dtype=int)
# data=Numeric.array(data) # for older PyGame that requires Numeric
pygame.init()  # crank up PyGame
pygame.display.set_caption("Simple Spectrograph")
screen = pygame.display.set_mode((windowWidth, fftsize/2))
world = pygame.Surface((windowWidth, fftsize/2), depth=8)  # MAIN SURFACE
world.set_palette(pal)
t_rec = threading.Thread(target=record)  # make thread for record()
t_rec.daemon = True  # daemon mode forces thread to quit with program
t_rec.start()  # launch thread
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