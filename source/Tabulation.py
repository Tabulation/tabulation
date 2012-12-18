
import sys
import pyaudio
import wave
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import * #floor, int16, fromstring, vstack, savetxt, fft

# TODOS
#1.Abgleichen der Frequenzen mit (inkl Toleranz ca 3-4+-) Array in dem Töne/Grifffrequenzen stehen
# und namen ausgeben
#2.Hemmschwelle einbauen Ton wird erst ab gewisser Lautstärke akzeptiert
#3. chibsch machen


exiting = False
class Window(QWidget):
    def __init__(self, parent = None):
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
        #print(exiting)

class Worker(QThread):

    def test(self):
        if exiting == True:
            global exiting
            exiting = False

    def __init__ (self, parent = None):

        QThread.__init__(self, parent)
        global exiting
        exiting = False

    def __del__(self):
        global exiting
        exiting = True
        #print(exiting)

    # def get_current_first_channel(self):
        # return self.first_channel

    # def get_current_device_nchannels(self):
        # return self.pa.get_device_info_by_index(self.device)['maxInputChannels']

    def runStart(self):
        self.start()

    def run(self):
        print("Starte Run")
        CHUNK = 1024 * 8
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
            #print(".")
            data = stream.read(CHUNK)
            frames.append(data)
            floatdata = fromstring(data, int16)[0::2] / (2. ** (16 - 1))
            fft_array = fft.fft(floatdata)
            #b = abs(fft_array)
            b = [abs(x) for x in fft_array][:4098]  #betrag, erste Haelfte
            m = max(b)
            for i, x in enumerate(b):
                if x > m / 30:  # umso hoeher mehr werte
                    #print(i, i*RATE/CHUNK, " "* int(100*x/m), "#")
                    if m == x:
                        mi = i
                        #print ("max: ", m , " bei ", mi , " ",  mi*RATE/CHUNK, " Hz")
                        KEYNOTE = mi * RATE / CHUNK
                        #methode mit unscharfer abgleichung fuer notenerkennung
                        print("Der Grundton betraegt: ", KEYNOTE, " Hz")
                #zeros(c)
            #print(data)
            #print(floatdata)

        #text_file = open("Output.txt", "w")
        #text_file.write(floatdata)
        #text_file.close()
        #savetxt('output.txt', floatdata, delimiter=',')
        #savetxt('fft.txt', fft_array, delimiter=',')
        #print("done recording *")
        #print(c)

        #b = [abs(x) for x in fft_array][:3072]  #betrag, erste Haelfte
        #m = max(b)
        #with open("kurve.txt", "w") as f:
            ##mi = -1
            #for i, x in enumerate(b):
                #if x > m/10: # umso hoeher mehr werte
                    #print(i, i*RATE/CHUNK, " "* int(100*x/m), "#", file=f)
                    #if m == x:
                        #mi = i
            #print ("max: ", m , " bei ", mi , "(",  mi*RATE/CHUNK, " Hz",  file=f)

        #a = get_device_count()
        #print(a)
        #print(floatdata)
        #numpyarray into string damit in txt file
        #import pdb; pdb.set_trace() #Python Debugger
        #dir (data)
        #print(pa.get_device_info_by_index(device))
        #str(data)
        #floatdata = frombytes(data, int16)
        #print(floatdata)

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


