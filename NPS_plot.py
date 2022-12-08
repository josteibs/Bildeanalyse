# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 13:45:05 2022

@author: josste
Program for plotting NPS
"""

import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib as mpl
import pydicom 
import glob
import numpy as np
import os
import cv2

working_directory = 'F:/Røntgen/Arbeidsmappe/2022/2022 Filtermatching_GUI/CT bilder av Catphan/Body' #os.getcwd()

### Window design
layout = [
    # import image series
    [sg.Text("Import image series:")],
    [sg.InputText(key='-FOLDER_PATH-', enable_events=True),
     sg.FolderBrowse(initial_folder=working_directory)],
    # View FOV
    [sg.Button("Check FOV", key='-FOV-', disabled=True)]
]
window = sg.Window("Noise Power Spectrum", layout, size=((450,300)))

### Functions and classes
# sort function
def sortImages(pathname):
    '''Function from Vilde
    Sort images in same directory'''
    sortDict = {}
    for path in glob.glob(pathname):
        ds = pydicom.dcmread(path, stop_before_pixels=True)
        sortDict[ds.SliceLocation] = path
        mpl.rc('figure', max_open_warning = 0)
    sortedKeys = sorted(sortDict.keys())
    return sortDict, sortedKeys 

class Images:
    def __init__(self, folder_path):
       self.sortDict, self.sortedKeys = sortImages(folder_path) #Sort images
       self.FOVcorner = 150
       self.FOVsize = 200
       
    def showFOV(self):
        # Using one of images to display FOV
        data0 = self.sortDict[self.sortedKeys[0]]
        dicom0 = pydicom.dcmread(data0)
        image0 = dicom0.pixel_array
        image0 = image0 * dicom0.RescaleSlope + dicom0.RescaleIntercept
        fig, ax = plt.subplots()
        im = ax.imshow(image0, cmap='Greys_r', vmin=-100, vmax=200)
        
        # Marking FOV
        rect = mpl.patches.Rectangle((self.FOVcorner, self.FOVcorner), self.FOVsize, self.FOVsize, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        plt.show()
        
        
        #fig, ax = plt.subplots()
        #im = ax.imshow(image0[self.FOVcorner:self.FOVcorner+self.FOVsize, self.FOVcorner:self.FOVcorner+self.FOVsize])
        #plt.show()
    
    def averageFOV(self):
        # Summing up FOV from images series and average
        averageFOV = np.zeros((self.FOVsize, self.FOVsize))
        self.N = len(self.sortedKeys)
        # FOV cube to contain the whole FOV.
        self.FOV_cube = np.empty((self.FOVsize, self.FOVsize, self.N))
        i = 0
        plt.figure()
        for key in self.sortedKeys:
            # Average FOV
            data = self.sortDict[key]
            dicom = pydicom.dcmread(data)
            image = dicom.pixel_array
            image = image * dicom.RescaleSlope + dicom.RescaleIntercept
            FOV = image[self.FOVcorner:self.FOVcorner+self.FOVsize, self.FOVcorner:self.FOVcorner+self.FOVsize]
            averageFOV += FOV
            
            # Making FOV cube
            self.FOV_cube[:,:,i] = FOV
            i+=1
        print(f'N: {self.N}')
        self.averageFOV = averageFOV/self.N
        plt.imshow(self.averageFOV, cmap='Greys_r') 
    
    def singleNPS(self):
        FOV_sub = self.FOV_cube[:,:,0] - self.averageFOV
        plt.figure()
        plt.imshow(FOV_sub, cmap='Greys_r')
        
        g = self.FOV_cube[:,0,0]
        g_bar = self.averageFOV[:,0]
        g_sub = g - g_bar
        
        '''
        plt.figure()
        plt.plot(g, label='g')
        plt.plot(g_bar, label='g_bar')
        plt.plot(g_sub, label='g_sub')
        plt.legend()
        plt.show()
        '''
    def setFOV(self):
        print('FOV')
    
    def NPS(self):
        print('NPS')
        
    


### GUI action
while True:
    event, values = window.read()
    
    if event == '-FOLDER_PATH-':
        window['-FOV-'].update(disabled=False)
        
    if event == '-FOV-':
        path = values['-FOLDER_PATH-'] + '/*'
        images = Images(path)
        images.showFOV()
        images.averageFOV()
        images.singleNPS()
        
        
    
    if event == sg.WIN_CLOSED:
        break
    
window.close()