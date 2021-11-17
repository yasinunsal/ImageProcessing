# image_viewer.py
import io
import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageTk, ImageOps
from skimage import data, exposure, img_as_float
from skimage import filters
from skimage.morphology import thin, area_opening, area_closing, diameter_closing, diameter_opening, erosion, flood_fill, black_tophat, white_tophat, dilation
from skimage.filters import threshold_otsu
from skimage.transform import resize, rotate, swirl, rescale, warp, SimilarityTransform
from skimage.exposure import rescale_intensity
from PyQt5 import QtGui
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import asyncio
import copy

root = tk.Tk()
root.iconbitmap("process.ico")  # changed icon
root.title("Image Processing")

window_width = 1000
window_height = 500

sign_image = Label(root, bg="black")
sign_image2 = Label(root, bg="black")

# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# find the center point
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)

# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(False, False)

# configure columns and rows
root.columnconfigure(0, weight=3)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=3)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)
root.rowconfigure(8, weight=1)
root.rowconfigure(9, weight=1)
root.rowconfigure(10, weight=2)
root.rowconfigure(11, weight=2)

mainMenu = ['Filter', 'Histogram', 'Transform', 'Rescale Intensity', 'Morphology']
mainMenuButtons = []
filtersArray = ['Prewitt', 'Farid', 'Meijering', 'Sato', 'Frangi', 'Hessian', 'Gaussian', 'Roberts', 'Sobel',
                'Unsharp Mask']
filterButtons = []
transformsArray = ['Resize', 'Rotate', 'Swirl', 'Rescale', 'Warp']
transformButtons = []
morphologiesArray = ['Thin', 'Area Opening', 'Area Closing', 'Diameter Opening', 'Diameter Closing', 'Erosion',
                     'Flood Fill',
                     'Black Top Hat', 'White Top Hat', 'Dilation']
morphologyButtons = []

def LoadImage():
    try:
        file_path = filedialog.askopenfilename()
        global image
        image = Image.open(file_path)
        imageDisplayed = image
        global photoWidthDpi
        global photoHeightDpi
        try:
            photoWidthDpi, photoHeightDpi = image.info['dpi']
        except:
            photoWidthDpi = photoHeightDpi = 96
        imageDisplayed.thumbnail(((1000 / 2.40), (800 / 2.40)))
        image = ImageOps.grayscale(image)
        photo = ImageTk.PhotoImage(imageDisplayed)
        image = np.array(image, dtype=np.uint8)
        global photoWidth
        photoWidth = photo.width()
        global photoHeight
        photoHeight = photo.height()

        sign_image.configure(image=photo)
        sign_image.image = photo
        sign_image.grid(column=0, row=0, rowspan=11, ipadx=1, ipady=1)

        sign_image2.configure(image=photo)
        sign_image2.image = photo
        sign_image2.grid(column=2, row=0, rowspan=11, ipadx=1, ipady=1)
    except:
        pass

def LoadPhoto(img):
    # img = plt.imshow(img, cmap="gray")
    fig = plt.Figure(figsize=((photoWidth / photoWidthDpi), (photoHeight / photoHeightDpi)))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot()
    ax.imshow(img, cmap="gray")
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('tight')
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    openedImage = Image.open(buf)
    # img = Image.fromarray(np.uint8(cm.gist_earth(img, bytes=True)))
    # img = ImageOps.grayscale(img)
    openedImage.thumbnail((photoWidth, photoHeight))
    photo = ImageTk.PhotoImage(openedImage)
    buf.close()
    print(photo.width())
    print(photo.height())
    sign_image2.configure(image=photo)
    sign_image2.image = photo
    sign_image2.grid(column=2, row=0, rowspan=11, ipadx=1, ipady=1)

def Prewitt():
    prewitt_image = filters.prewitt(image)
    LoadPhoto(prewitt_image)

def Farid():
    farid_image = filters.farid(image)
    LoadPhoto(farid_image)

def Meijering():
    meijering_image = filters.meijering(image)
    LoadPhoto(meijering_image)

def Sato():
    sato_image = filters.sato(image)
    LoadPhoto(sato_image)

def Frangi():
    frangi_image = filters.frangi(image)
    LoadPhoto(frangi_image)

def Hessian():
    hessian_image = filters.hessian(image)
    LoadPhoto(hessian_image)

def Gaussian():
    gaussian_image = filters.gaussian(image)
    LoadPhoto(gaussian_image)

def Roberts():
    roberts_image = filters.roberts(image)
    LoadPhoto(roberts_image)

def Sobel():
    sobel_image = filters.sobel(image)
    LoadPhoto(sobel_image)

def UnsharpMask():
    unsharp_mask_image = filters.unsharp_mask(image)
    LoadPhoto(unsharp_mask_image)

def Resize():
    print("Transform1")

def Rotate():
    print("Transform2")

def Swirl():
    print("Transform3")

def Rescale():
    print("Transform4")

def Warp():
    print("Transform5")

def Thin():
    thin_image = thin(image)
    LoadPhoto(thin_image)

def AreaOpening():
    area_opening_image = area_opening(image)
    LoadPhoto(area_opening_image)

def AreaClosing():
    area_closing_image = area_closing(image)
    LoadPhoto(area_closing_image)

def DiameterOpening():
    diameter_opening_image = diameter_opening(image)
    LoadPhoto(diameter_opening_image)

def DiameterClosing():
    diameter_closing_image = diameter_closing(image)
    LoadPhoto(diameter_closing_image)

def Erosion():
    erosion_image = erosion(image)
    LoadPhoto(erosion_image)

def FloodFill():
    print("Morphology7")

def BlackTopHat():
    black_tophat_image = black_tophat(image)
    LoadPhoto(black_tophat_image)

def WhiteTopHat():
    white_tophat_image = white_tophat(image)
    LoadPhoto(white_tophat_image)

def Dilation():
    dilation_image = dilation(image)
    LoadPhoto(dilation_image)

def Filter():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(filterButtons)):
        filterButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=10, command=lambda: [ForgetGrid(backButton, "filter")])
    backButton.grid(column=1, row=10, ipady=10)

def Transform():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(transformButtons)):
        transformButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=10, command=lambda: [ForgetGrid(backButton, "transform")])
    backButton.grid(column=1, row=5, ipady=10)

def Morphology():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(morphologyButtons)):
        morphologyButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=10, command=lambda: [ForgetGrid(backButton, "morphology")])
    backButton.grid(column=1, row=10, ipady=10)

def ForgetGrid(btn, processType):
    if (processType == "transform"):
        for i in transformButtons:
            i.grid_forget()
    elif (processType == "filter"):
        for i in filterButtons:
            i.grid_forget()
    elif (processType == "morphology"):
        for i in morphologyButtons:
            i.grid_forget()
    btn.grid_forget()
    MainMenu()

def Construct():
    for x in range(len(mainMenu)):
        if mainMenu[x] == "Filter":
            temp = ttk.Button(root, text=mainMenu[x], command=Filter)
        elif mainMenu[x] == "Histogram":
            temp = ttk.Button(root, text=mainMenu[x], command=Histogram)
        elif mainMenu[x] == "Transform":
            temp = ttk.Button(root, text=mainMenu[x], command=Transform)
        elif mainMenu[x] == "Rescale Intensity":
            temp = ttk.Button(root, text=mainMenu[x], command=RescaleIntensity)
        elif mainMenu[x] == "Morphology":
            temp = ttk.Button(root, text=mainMenu[x], command=Morphology)
        temp.grid(column=1, row=x)
        mainMenuButtons.append(temp)
        temp.grid_forget()

    for z in range(len(filtersArray)):
        if filtersArray[z] == "Prewitt":
            temp = ttk.Button(root, text=filtersArray[z], command=Prewitt)
        elif filtersArray[z] == "Farid":
            temp = ttk.Button(root, text=filtersArray[z], command=Farid)
        elif filtersArray[z] == "Meijering":
            temp = ttk.Button(root, text=filtersArray[z], command=Meijering)
        elif filtersArray[z] == "Sato":
            temp = ttk.Button(root, text=filtersArray[z], command=Sato)
        elif filtersArray[z] == "Frangi":
            temp = ttk.Button(root, text=filtersArray[z], command=Frangi)
        elif filtersArray[z] == "Hessian":
            temp = ttk.Button(root, text=filtersArray[z], command=Hessian)
        elif filtersArray[z] == "Gaussian":
            temp = ttk.Button(root, text=filtersArray[z], command=Gaussian)
        elif filtersArray[z] == "Roberts":
            temp = ttk.Button(root, text=filtersArray[z], command=Roberts)
        elif filtersArray[z] == "Sobel":
            temp = ttk.Button(root, text=filtersArray[z], command=Sobel)
        elif filtersArray[z] == "Unsharp Mask":
            temp = ttk.Button(root, text=filtersArray[z], command=UnsharpMask)
        temp.grid(column=1, row=z)
        filterButtons.append(temp)
        temp.grid_forget()

    for q in range(len(transformsArray)):
        if transformsArray[q] == "Resize":
            temp = ttk.Button(root, text=transformsArray[q], command=Resize)
        elif transformsArray[q] == "Rotate":
            temp = ttk.Button(root, text=transformsArray[q], command=Rotate)
        elif transformsArray[q] == "Swirl":
            temp = ttk.Button(root, text=transformsArray[q], command=Swirl)
        elif transformsArray[q] == "Rescale":
            temp = ttk.Button(root, text=transformsArray[q], command=Rescale)
        elif transformsArray[q] == "Warp":
            temp = ttk.Button(root, text=transformsArray[q], command=Warp)
        temp.grid(column=1, row=q)
        transformButtons.append(temp)
        temp.grid_forget()

    for c in range(len(morphologiesArray)):
        if morphologiesArray[c] == "Thin":
            temp = ttk.Button(root, text=morphologiesArray[c], command=Thin)
        elif morphologiesArray[c] == "Area Opening":
            temp = ttk.Button(root, text=morphologiesArray[c], command=AreaOpening)
        elif morphologiesArray[c] == "Area Closing":
            temp = ttk.Button(root, text=morphologiesArray[c], command=AreaClosing)
        elif morphologiesArray[c] == "Diameter Opening":
            temp = ttk.Button(root, text=morphologiesArray[c], command=DiameterOpening)
        elif morphologiesArray[c] == "Diameter Closing":
            temp = ttk.Button(root, text=morphologiesArray[c], command=DiameterClosing)
        elif morphologiesArray[c] == "Erosion":
            temp = ttk.Button(root, text=morphologiesArray[c], command=Erosion)
        elif morphologiesArray[c] == "Flood Fill":
            temp = ttk.Button(root, text=morphologiesArray[c], command=FloodFill)
        elif morphologiesArray[c] == "Black Top Hat":
            temp = ttk.Button(root, text=morphologiesArray[c], command=BlackTopHat)
        elif morphologiesArray[c] == "White Top Hat":
            temp = ttk.Button(root, text=morphologiesArray[c], command=WhiteTopHat)
        elif morphologiesArray[c] == "Dilation":
            temp = ttk.Button(root, text=morphologiesArray[c], command=Dilation)
        temp.grid(column=1, row=c)
        morphologyButtons.append(temp)
        temp.grid_forget()

def MainMenu():
    for x in range(len(mainMenuButtons)):
        mainMenuButtons[x].grid(column=1, row=x)

def Histogram():
    print("Histogram")

def RescaleIntensity():
    print("Rescale Intensity")


loadButton = ttk.Button(root, text='Load Image', width=20, command=LoadImage)
loadButton.grid(column=1, row=11, ipady=10)

Construct()
MainMenu()

root.mainloop()