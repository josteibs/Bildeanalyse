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
import scipy.fft as fft 

working_directory = 'F:/Røntgen/Arbeidsmappe/2022/2022 Filtermatching_GUI/CT bilder av Catphan/Body' #os.getcwd()

### Window design
layout = [
    # import image series
    [sg.Text("Import image series:")],
    [sg.InputText(key='-FOLDER_PATH-', enable_events=True),
     sg.FolderBrowse(initial_folder=working_directory)],
    # View ROI
    [sg.Button("Check ROI", key='-ROI-', disabled=True)]
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
       self.ROIcorner = 150
       self.ROIsize = 200
       
    def showROI(self):
        # Using one of images to display ROI
        data0 = self.sortDict[self.sortedKeys[0]]
        self.dicom0 = pydicom.dcmread(data0)
        image0 = self.dicom0.pixel_array
        image0 = image0 * self.dicom0.RescaleSlope + self.dicom0.RescaleIntercept
        fig, ax = plt.subplots()
        im = ax.imshow(image0, cmap='Greys_r', vmin=-100, vmax=200)
        
        # Marking ROI
        rect = mpl.patches.Rectangle((self.ROIcorner, self.ROIcorner), self.ROIsize, self.ROIsize, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        plt.show()
        
        
        #fig, ax = plt.subplots()
        #im = ax.imshow(image0[self.ROIcorner:self.ROIcorner+self.ROIsize, self.ROIcorner:self.ROIcorner+self.ROIsize])
        #plt.show()
    
    def averageROI(self):
        # Summing up ROI from images series and average
        averageROI = np.zeros((self.ROIsize, self.ROIsize))
        self.N = len(self.sortedKeys)
        # ROI cube to contain the whole ROI.
        self.ROI_cube = np.empty((self.ROIsize, self.ROIsize, self.N))
        i = 0
        plt.figure()
        for key in self.sortedKeys:
            # Average ROI
            data = self.sortDict[key]
            dicom = pydicom.dcmread(data)
            image = dicom.pixel_array
            image = image * dicom.RescaleSlope + dicom.RescaleIntercept
            ROI = image[self.ROIcorner:self.ROIcorner+self.ROIsize, self.ROIcorner:self.ROIcorner+self.ROIsize]
            averageROI += ROI
            
            # Making ROI cube
            self.ROI_cube[:,:,i] = ROI
            i+=1
        print(f'N: {self.N}')
        self.averageROI = averageROI/self.N
        plt.imshow(self.averageROI, cmap='Greys_r') 
    
    def singleNPS(self):
        # Get the pixel size of the image series
        px_sz = self.dicom0[0x28, 0x30]
        px_sz_row = px_sz[0] # pixel row spacing in mm
        px_sz_col = px_sz[1] # pixel column spacing in mm
        
        # frame for summing fft images
        self.averageROI_fft = np.zeros((self.ROIsize, self.ROIsize))
        # summing fft of ROIs
        for i in range(self.N):
            ROI_sub = self.ROI_cube[:,:,i] - self.averageROI
            ROI_fft = fft.fft2(ROI_sub)
            ROI_fft_mod2 = np.real(ROI_fft)**2 + np.imag(ROI_fft)**2*(px_sz_row*px_sz_col)/(self.ROIsize**2)
            self.averageROI_fft += ROI_fft_mod2
        self.averageROI_fft = self.averageROI_fft/self.N
        plt.figure()
        plt.imshow(self.averageROI_fft, cmap='Greys_r', vmin=min(self.averageROI_fft[50,:]), vmax=max(self.averageROI_fft[50,:]))
        plt.show()
        
        
        
        '''
        g = self.ROI_cube[:,0,0]
        g_bar = self.averageROI[:,0]
        g_sub = g - g_bar
        
        
        plt.figure()
        plt.plot(g, label='g')
        plt.plot(g_bar, label='g_bar')
        plt.plot(g_sub, label='g_sub')
        plt.legend()
        plt.show()
        '''
    def setROI(self):
        print('ROI')
    
    def NPS(self):
        print('NPS')
        
    


### GUI action
while True:
    event, values = window.read()
    
    if event == '-FOLDER_PATH-':
        window['-ROI-'].update(disabled=False)
        
    if event == '-ROI-':
        path = values['-FOLDER_PATH-'] + '/*'
        images = Images(path)
        images.showROI()
        images.averageROI()
        images.singleNPS()
        
        
    
    if event == sg.WIN_CLOSED:
        break
    
window.close()