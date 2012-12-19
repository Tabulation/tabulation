
import sys
import pyaudio
import wave
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import * #floor, int16, fromstring, vstack, savetxt, fft

# TODOS
#1.Abgleichen der Frequenzen mit (inkl Toleranz ca 3-4+-) Array in dem Töne/Grifffrequenzen stehen
# und namen ausgeben --> weitere Instruktionen in Kommentaren in aufnahme-schleife
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
            b = [abs(x) for x in fft_array][:4098]  #berag, erste Haelfte
            m = max(b)


            frequenzTabelle = [65.4064, 69.2957, 73.4162, 77.7817, 82.4069, 87.3071, 92.4986, 97.9989, 103.826, 110.000, 116.541, 123.471, 130.813, 138.591, 146.832, 155.563, 164.814, 174.614, 184.997, 195.998, 207.652, 220.000, 233.082, 246.942, 261.626, 277.183, 293.665, 311.127, 329.628, 349.228, 369.994, 391.995, 415.305, 440.000, 466.164, 493.883, 523.251, 554.365, 587.330, 622.254, 659.255, 698.456, 739.989, 783.991, 830.609, 880.000, 932.328, 987.767, 1046.50, 1108.73, 1174.66, 1244.51, 1318.51, 1396.91, 1479.98, 1567.98, 1661.22, 1760.00, 1864.66, 1957.53, 2093.00, 2217.46, 2349.32, 2489.02, 2637.02, 2793.83, 2959.96, 3135.96, 3322.44, 3520.00, 3729.31, 3951.07, 4186.01]
            Notentabelle = [X,X,X,X,E0,E1,E2,E3,E4,E5,E6,E7,E8,E9,E10,E11,E12]

            for i, x in enumerate(b):
                if x > m / 30:  # umso hoeher mehr werte
                    #print(i, i*RATE/CHUNK, " "* int(100*x/m), "#")
                    if m == x:
                        mi = i
                        #print ("max: ", m , " bei ", mi , " ",  mi*RATE/CHUNK, " Hz")
                        #Nach dem Errechnen eine Methode die das Ganze mit einer Liste abgleicht mit Toleranz
                        KEYNOTE = mi * RATE / CHUNK
                        #methode mit unscharfer abgleichung fuer notenerkennung
                        print("Der Grundton betraegt: ", KEYNOTE, " Hz")


                        #findeTon(KEYNOTE)
                        #frequenzTabelle.count(frequenz)
                        #frequenzTabelle.index(KEYNOTE)
                        #print("Frequenz kommt vor ", frequenzTabelle.count(KEYNOTE))
                        #print int(round(8359980, -2))
                        #print (round(KEYNOTE, -2))

                        #frequentabelle mit  KEYNOTE durchgehen, ersten größeren wert nehmen
                        #index dieses wertes finden, und des wertes darunter
                        #verhältnis ausrechnen, den wert nehmen welchen verhältnis besser ist
                        # tadaa, richtige note, mithilfe des index auf notentablle(derindex) zugreifen
                        #Profit!


            #print(data)
            #print(floatdata)

        #text_file = open("Output.txt", "w")0
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


