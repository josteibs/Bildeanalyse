# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 13:45:05 2022

@author: Jostein Steffensen
Program for plotting NPS
"""


import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import pydicom 
import PySimpleGUI as sg
import scipy.fft as fft

from sort_images import sortImages

working_directory = 'F:/Røntgen/Arbeidsmappe/2022/2022 Filtermatching_GUI/CT bilder av Catphan/Body' #os.getcwd()

### Window design
layout = [
    # import image series
    [sg.Text("Import image series:")],
    [sg.InputText(key='-FOLDER_PATH-', enable_events=True),
     sg.FolderBrowse(initial_folder=working_directory)],
    # View ROI
    [sg.Button("Check ROI", key='-ROI-', disabled=True)],
    [sg.Button("2D NPS", key='-2DNPS-', disabled=True)],
    [sg.Button("NPS", key='-NPS-', disabled=True)]
]
window = sg.Window("Noise Power Spectrum", layout, size=((550,300)))

### Functions and classes
# sort function

class Images:
    def __init__(self, folder_path):
       self.sortDict, self.sortedKeys = sortImages(folder_path) #Sort images
       self.ROIcorner = 150
       self.ROIsize = 201
       # Using first image to display ROI
       data0 = self.sortDict[self.sortedKeys[0]]
       self.dicom0 = pydicom.dcmread(data0)
    
    # Display first image with ROI
    def showROI(self):
        
        image0 = self.dicom0.pixel_array
        image0 = image0 * self.dicom0.RescaleSlope + self.dicom0.RescaleIntercept
        fig, ax = plt.subplots()
        im = ax.imshow(image0, cmap='Greys_r', vmin=-100, vmax=200)
        
        # Marking ROI
        rect = mpl.patches.Rectangle((self.ROIcorner, self.ROIcorner), self.ROIsize, self.ROIsize, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        plt.show()
        
        #2D match
        #plt.figure()
        #plt.imshow(surface_fit(image0[self.ROIcorner:self.ROIcorner+self.ROIsize, self.ROIcorner:self.ROIcorner+self.ROIsize]))
        #plt.show()
        
        # Code to only display ROI-image.
        fig, ax = plt.subplots()
        im = ax.imshow(image0[self.ROIcorner:self.ROIcorner+self.ROIsize, self.ROIcorner:self.ROIcorner+self.ROIsize])
        plt.show()
    
    # Making 3d array of ROI
    def ROIcube(self):
        self.N = len(self.sortedKeys)
        # ROI cube to contain the whole ROI.
        self.ROI_cube = np.empty((self.ROIsize, self.ROIsize, self.N))
        i = 0
        for key in self.sortedKeys:
            data = self.sortDict[key]
            dicom = pydicom.dcmread(data)
            image = dicom.pixel_array
            image = image * dicom.RescaleSlope + dicom.RescaleIntercept
            ROI = image[self.ROIcorner:self.ROIcorner+self.ROIsize, self.ROIcorner:self.ROIcorner+self.ROIsize]
            
            # Making ROI cube
            self.ROI_cube[:,:,i] = ROI
            i+=1
        print(f'N: {self.N}')
    
    # Calulating 2D NPS
    def fft2_avg(self):
        # Get the pixel size of the image series
        px_sz = self.dicom0[0x28, 0x30]
        px_sz_row = px_sz[0] # pixel row spacing in mm
        px_sz_col = px_sz[1] # pixel column spacing in mm
        
        # frame for summing fft images
        self.averageROI_fft = np.zeros((self.ROIsize, self.ROIsize))
        # summing fft of ROIs
        for i in range(self.N):
            # Best linear fit
            # ROI_fit = curve_fit(func, self.ROI_cube[:,:,i])
            
            #FFT of subtracted ROI
            ROI_sub = self.ROI_cube[:,:,i] - np.mean(self.ROI_cube[:,:,i])
            ROI_fft = fft.fft2(ROI_sub)
            ROI_fft_mod2 = (np.real(ROI_fft)**2 + np.imag(ROI_fft)**2)*(px_sz_row*px_sz_col)/(self.ROIsize**2)
            self.averageROI_fft += ROI_fft_mod2
        self.averageROI_fft = fft.fftshift(self.averageROI_fft/self.N)
    
    # Displaying 2D NPS
    def NPS_2D(self):
        plt.figure()
        plt.imshow(self.averageROI_fft, cmap='Greys_r', vmin=min(self.averageROI_fft[50,:]), vmax=max(self.averageROI_fft[50,:]))
        plt.show()
      
    # Radial average of 2D NPS    
    def radial_avg(self):
        # Creds to Naveen Venkatesan for the idea for this function
        cen_x = 100
        cen_y = 100
        
        # Find radial distances 
        [X, Y] = np.meshgrid(np.arange(self.ROIsize)-cen_x, np.arange(self.ROIsize)-cen_y)
        R = np.sqrt(np.square(X)+np.square(Y))
        
        rad = np.arange(1, np.max(R), 1)
        intensity = np.zeros(len(rad))
        index = 0
        bin_size = 1
        
        for i in rad:
            mask = (np.greater(R, i - bin_size) & np.less(R, i + bin_size))
            rad_values = self.averageROI_fft[mask]
            intensity[index] = np.mean(rad_values)
            index += 1
            
        # Create figure and add subplot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # Plot data
        ax.plot(rad, intensity, linewidth=2)
        # Edit axis labels
        ax.set_xlabel('Radial Distance', labelpad=10)
        ax.set_ylabel('Average Intensity', labelpad=10)
        
        '''
        # Code to plot a 1D-line in the image and disply signal - average.
        g = self.ROI_cube[:,0,0]
        g_bar = np.mean(self.ROI_cube[:,:,0])# self.averageROI[:,0]
        g_sub = g - g_bar
        
        
        plt.figure()
        plt.plot(g, label='g')
        plt.plot(g_bar, label='g_bar')
        plt.plot(g_sub, label='g_sub')
        plt.legend()
        plt.show()
        '''
      
    # Not used yet    
    def setROI(self):
        print('ROI')
    
    def NPS(self):
        print('NPS')
        
    


### GUI action
while True:
    event, values = window.read()
    
    if event == '-FOLDER_PATH-':
        window['-ROI-'].update(disabled=False)
        window['-2DNPS-'].update(disabled=False)
        window['-NPS-'].update(disabled=False)
        
        # Make an Images class object
        path = values['-FOLDER_PATH-'] + '/*'
        images = Images(path)
        
        # NPS calculations
        images.ROIcube()
        images.fft2_avg()
        
    if event == '-ROI-':
        images.showROI()
        
    if event == '-2DNPS-':
        images.NPS_2D()
        
    if event == '-NPS-':
        images.radial_avg()
        
    
    if event == sg.WIN_CLOSED:
        break
    
window.close()