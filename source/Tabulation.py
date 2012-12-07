# -*- coding: utf-8 -*-

import sys
import pyaudio
import wave
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import floor, int16, fromstring, vstack, savetxt, fft

exiting = False


def analysis(floatdata):
    #print("in a")
    #bet = abs(fft.fft(floatdata))[:CHUNK/2]
    #maxi = max(bet)
    #for i, x in enumerate(bet):
        #if x > (maxi / 10):
            #return(i, i * RATE / CHUNK, " " * int(100 * x / maxi), "#")
    return("lol")


class Window(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.thread = Worker()
        label = QLabel(self.tr("Starten sie Ihre Aufnahme"))
        self.startButton = QPushButton(self.tr("&Start"))
        self.stopButton = QPushButton(self.tr("&Stop"))
        self.viewer = QLabel()
        self.viewer.setFixedSize(300, 300)
        self.connect(self.thread, SIGNAL("finished()"), self.updateUi)
        self.connect(self.thread, SIGNAL("terminated()"), self.updateUi)
        self.connect(self.thread, SIGNAL("output(QRect, QImage)"), self.addImage)
        self.connect(self.startButton, SIGNAL("clicked()"), self.startRecording)
        self.connect(self.stopButton, SIGNAL("clicked()"), self.__del__)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        #layout.addWidget(self.spinBox, 0, 1)
        layout.addWidget(self.startButton, 0, 2)
        layout.addWidget(self.stopButton, 3, 4)
        layout.addWidget(self.viewer, 1, 0, 1, 3)
        self.setLayout(layout)

        self.setWindowTitle(self.tr("Tabulation Aufnahme"))

    def startRecording(self):
        self.startButton.setEnabled(False)
        self.thread.runStart()

    def addImage(self, rect, image):
        pixmap = self.viewer.pixmap()
        painter = QPainter()
        painter.begin(pixmap)
        painter.drawImage(rect, image)
        painter.end()
        self.viewer.update(rect)

    def updateUi(self):
        self.startButton.setEnabled(True)

    def __del__(self):
        global exiting
        exiting = True
        print(exiting)


class Worker(QThread):

    def test(self):
        if exiting:
            global exiting
            exiting = False

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        global exiting
        exiting = False

    def __del__(self):
        global exiting
        exiting = True
        print(exiting)

    # def get_current_first_channel(self):
        # return self.first_channel

    # def get_current_device_nchannels(self):
        # return self.pa.get_device_info_by_index(self.device)['maxInputChannels']

    def runStart(self):
        self.start()

    def run(self):
        print("Starte Run")
        CHUNK = 1024 * 2
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        #RECORD_SECONDS = 10
        WAVE_OUTPUT_FILENAME = "aufnahme122.wav"
        #channel = self.get_current_first_channel()
        #nchannels = self.get_current_device_nchannels()
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []
        self.test()
        #print(exiting)
        while not exiting:
            data = stream.read(CHUNK)
            frames.append(data)
            floatdata = fromstring(data, int16)[0::2] / (2. ** (16 - 1))
            bet = abs(fft.fft(floatdata))[:CHUNK/2]
            maxi = max(bet)
            for i, x in enumerate(bet):
                if x > (maxi / 10):
                    print(i, i * RATE / CHUNK, " " * int(100 * x / maxi), "#")
            #print(analysis(floatdata))
            fft_array = fft.fft(floatdata)

        #ext_file = open("Output.txt", "w")
        #text_file.write(floatdata)
        #text_file.close()
        #savetxt('output.txt', floatdata, delimiter=',')
        savetxt('fft.txt', fft_array, delimiter=',')
        print("done recording *")

        b = [abs(x) for x in fft_array][:CHUNK/2]#betrag, erste Hälfte
        m = max(b)
        with open("kurve.txt", "w") as f:
            #mi = -1
            for i, x in enumerate(b):
                if x > (m / 10):        # umso hoeher mehr werte
                    f.write(i, i * RATE / CHUNK, " " * int(100 * x / m), "#")
                    #if m == x:
                        #mi = i
            #print ("max: ", m , " bei ", mi , "(",  mi*RATE/CHUNK, " Hz",  file=f)

        #a = get_device_count()
        #print(a)
        #numpyarray into string damit in txt file
        #import pdb; pdb.set_trace() #Python Debugger
        #dir (data)
        #print(pa.get_device_info_by_index(device))
        #str(data)
        #floatdata = frombytes(data, int16)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
