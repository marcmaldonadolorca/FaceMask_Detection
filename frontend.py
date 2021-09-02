#!/usr/bin/env python
# coding: utf-8


import cv2
import os
import re

from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter.messagebox import showinfo
import threading
from imutils.video import VideoStream
import json

import base64
import requests

"""El código contiene una clase, PhotoBoothApp, creada para la interfaz del programa. Se utilizaa tkinter para dar formato a la interfaz."""

class PhotoBoothApp:
    def __init__(self, vs, outputPath):
        """La intefaz se genera y se da formato aquí, los botones, textos y camara son añadidos a la ventana."""
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None
        
        w = tki.Label(self.root, text="¡Por favor, acérquese y centre su cara!", font = "Helvetica 20 bold")
        w.pack(side="top", fill="both", expand="yes", padx=10,
                 pady=10)
        # create a button, that when pressed, will take the current
        # frame and save it to file
        x = tki.Label(self.root, text="¡Por favor, cuando este listo, presione 'Foto!'", font = "Helvetica 16 bold")
        x.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)
        btn = tki.Button(self.root, text="Foto!",
                         command=self.takeSnapshot, font = "Helvetica 20 bold")
        btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)
        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("Detector de Mascarillas")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        

    def videoLoop(self):
        # DISCLAIMER:
        # I'm not a GUI developer, nor do I even pretend to be. This
        # try/except statement is a pretty ugly hack to get around
        # a RunTime error that Tkinter throws due to threading
        """Código necesario para la entrada de vidieo de la cámara."""
        try:
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():
                # grab the frame from the video stream and resize it to
                # have a maximum width of 300 pixels
                self.frame = self.vs.read()
                
                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                # if the panel is not None, we need to initialize it
                if self.panel is None:
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                # otherwise, simply update the panel
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def takeSnapshot(self):
        """Parte de del evento al clicar en el botón de Foto!. Se hacen la llamada a la funcion creada en Google Cloud y posteriormente, se extraen los resultados y se imprimen en la pantalla"""
        # grab the current timestamp and use it to construct the
        # output path
        filename = "foto.json"
        
        # save the file
        if self.frame is not None:
            
            #img = cv2.imread('./0.jpg')
            string = base64.b64encode(cv2.imencode('.png', self.frame)[1]).decode()
            request = {
                'img': string
            }
            
            
            with open('Imagencara.json', 'w') as outfile:
                json.dump(request, outfile, ensure_ascii=False, indent=4)
            
            url = 'https://us-central1-sm-project-310409.cloudfunctions.net/function-2'
            payload = json.dumps(request, indent=(4))
            headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
            r = requests.post(url, data=payload, headers=headers)
            
            
            print("request")
            print(str(r.content))
            
            showinfo('Resultado: ', str(r.content))
            if re.search("Correcta", str(r.content)):
                showinfo('Mensaje: ','¡Puede pasar!')
            elif re.search("Incorrecta", str(r.content)):
                showinfo('Mensaje: ','¡Por favor, antes de pasar, pongase la mascarilla correctamente!')

            

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()

"""Bucle principal del programa, aquí se llama la camara y a la clase para interfaz. También importa el archivo con las credenciales necesarias para Google Cloud"""

if __name__ == '__main__':
    file_path = "foto.jpg"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sm-project-310409-a97e57d6fe22.json"
    print("[INFO] warming up camera...")
    vs = VideoStream(src=0).start()

    # start the app
    pba = PhotoBoothApp(vs, '')
    pba.root.mainloop()




