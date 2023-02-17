# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 10:49:30 2023

@author: Jostein Steffensen
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import curve_fit

# polynomial fit
def func(x,y,a,b,c,d,e):
    return a*(x-c) + b*y

# Function passed to curve_fit
def _func(M, *args):
    x, y = M
    arr = np.zeros(x.shape)
    arr = func(x, y, *args)
    return arr

# 2D fit for images
def surface_fit(image):
    x_dim = image.shape[1]
    y_dim = image.shape[0]
    print(x_dim)
    print(y_dim)
    x = np.arange(0, x_dim, 1)
    y = np.arange(0, y_dim, 1)
    X, Y = np.meshgrid(x, y)
    xdata = np.vstack((X.ravel(), Y.ravel()))
    popt, pcov = curve_fit(_func, xdata, image.ravel(), (1, 1, 1, 1, 1))
    print(popt)
    print('------------------------------------')
    print(*popt)
    fit = np.zeros(image.shape)
    fit = func(X, Y, *popt)
    plt.figure()
    plt.imshow(fit, cmap='seismic')
    plt.show()
    return fit