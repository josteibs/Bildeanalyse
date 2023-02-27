# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 13:45:05 2022

@author: Jostein Steffensen
Program for plotting NPS
"""


import os
import PySimpleGUI as sg

from image_calc import Images

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