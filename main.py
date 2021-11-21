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
from skimage.morphology import thin, area_opening, area_closing, diameter_closing, diameter_opening, erosion, \
    flood_fill, black_tophat, white_tophat, dilation
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
import re

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
root.rowconfigure(10, weight=3)
# root.rowconfigure(11, weight=2)


mainMenu = ['Filter', 'Histogram', 'Transform', 'Rescale Intensity', 'Morphology']
mainMenuButtons = []
histogramButtons = []
filtersArray = ['Prewitt', 'Farid', 'Meijering', 'Sato', 'Frangi', 'Hessian', 'Gaussian', 'Roberts', 'Sobel',
                'Unsharp Mask']
filterButtons = []
transformsArray = ['Resize', 'Rotate', 'Swirl', 'Rescale', 'Pyramid Reduce']
transformButtons = []
morphologiesArray = ['Thin', 'Area Opening', 'Area Closing', 'Diameter Opening', 'Diameter Closing', 'Erosion',
                     'Flood Fill',
                     'Black Top Hat', 'White Top Hat', 'Dilation']
morphologyButtons = []
rescaleIntensityButtons = []
resizeArray = ['Height Entry', 'Width', 'Resize']
resizeButtons = []
rotateArray = ['Angle', 'Angle Entry', 'Rotate']
rotateButtons = []
swirlArray = ['Rotation', 'Rotation Entry', 'Strength', 'Strength Entry', 'Radius', 'Radius Entry', 'Swirl']
swirlButtons = []
rescaleArray = ['Scale', 'Scale Entry', 'Rescale']
rescaleButtons = []
pyramidReduceArray = ['Downscale', 'Downscale Entry', 'Pyramid Reduce']
pyramidReduceButtons = []


def Click(entry, message):
    if (entry.get() == message):
        entry.delete(0, 'end')
    if (message == "Angle"):
        entry.configure(validate="key", validatecommand=(entry.register(ValidationFloat), '%P'))
    else:
        entry.configure(validate="key", validatecommand=(entry.register(Validation), '%P', '%d'))


def Leave(entry, message):
    entry.configure(validate="none", validatecommand="none")
    if (entry.get() == "" and root.focus_get()['text'] != "Back"):
        entry.delete(0, 'end')
        entry.insert(0, message)


def Unmap(entry, message):
    entry.configure(validate="none", validatecommand="none")
    entry.delete(0, 'end')
    entry.insert(0, message)


def Validation(inStr, acttyp):
    if acttyp == '1':  # insert
        if not inStr.isdigit():
            return False
    return True


def ValidationFloat(string):
    regex = re.compile(r"(\-)?[0-9.]*$")
    result = regex.match(string)
    return (string == ""
            or (string.count('-') <= 1
                and string.count('.') <= 1
                and result is not None
                and result.group(0) != ""))


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
        ttk.Button(root, text='Save Image', width=17, command=LoadImage).place(x=735, y=450)
    except:
        pass


def LoadPhoto(img, h=0, w=0, type="Image", thresh=""):
    # img = plt.imshow(img, cmap="gray")
    if (h == 0 or w == 0):
        fig = plt.Figure(figsize=((photoWidth / photoWidthDpi), (photoHeight / photoHeightDpi)))
    else:
        fig = plt.Figure(figsize=((h / photoWidthDpi), (w / photoHeightDpi)))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot()
    if (type == "Histogram"):
        ax.hist(img.ravel(), bins=256)
        ax.set_title('Histogram')
        ax.axvline(thresh, color='r')
    elif (type == "Thresholded"):
        ax.imshow(img, cmap='gray')
        ax.set_title('Thresholded')
    else:
        ax.imshow(img, cmap="gray")
    if (type != "Histogram"):
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax.axis('tight')
        ax.axis('off')
    canvas.show()
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
    sato_image = filters.sato(image, mode='reflect')
    LoadPhoto(sato_image)


def Frangi():
    frangi_image = filters.frangi(image)
    LoadPhoto(frangi_image)


def Hessian():
    hessian_image = filters.hessian(image, mode='reflect')
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


def SwirlImage():
    print("Transform3")


def RescaleImage():
    print("Transform4")


def PyramidReduceImage():
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


def Resize(height, width):
    resized_image = resize(image, (int(height), int(width)))
    LoadPhoto(resized_image, int(height), int(width))


def Rotate():
    print("Rotate")


def Swirl():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(swirlButtons)):
        swirlButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=15, command=lambda: [ForgetGrid(backButton, "swirl")])
    backButton.grid(column=1, row=10)


def Rescale():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(rescaleButtons)):
        rescaleButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=15, command=lambda: [ForgetGrid(backButton, "rescale")])
    backButton.grid(column=1, row=10)


def PyramidReduce():
    for i in mainMenuButtons:
        i.grid_forget()
    for x in range(len(pyramidReduceButtons)):
        pyramidReduceButtons[x].grid(column=1, row=x)
    backButton = ttk.Button(root, text="Back", width=15, command=lambda: [ForgetGrid(backButton, "pyramidReduce")])
    backButton.grid(column=1, row=10)


def Histogram():
    thresh = threshold_otsu(image)
    LoadPhoto(image, type="Histogram", thresh=thresh)


def Threshold():
    thresh = threshold_otsu(image)
    binary = image > thresh
    LoadPhoto(binary, type="Thresholded")


def ReplaceGrid(buttonArray):
    for widget in root.winfo_children():
        if (widget.winfo_class() != "Label"):
            if (widget['text'] == "Back"):
                widget.place_forget()
            else:
                widget.grid_forget()

    for x in range(len(buttonArray)):
        if ((buttonArray[x])['text'] == "Back"):
            buttonArray[x].place(x=443.3, y=450)
        else:
            buttonArray[x].grid(column=1, row=x)


def Construct():
    mainMenuButtons.append(ttk.Button(root, width=17, text="Filter", command=lambda: ReplaceGrid(filterButtons)))
    mainMenuButtons.append(ttk.Button(root, width=17, text="Histogram", command=lambda: ReplaceGrid(histogramButtons)))
    mainMenuButtons.append(ttk.Button(root, width=17, text="Transform", command=lambda: ReplaceGrid(transformButtons)))
    mainMenuButtons.append(
        ttk.Button(root, width=16, text="Rescale Intensity", command=lambda: ReplaceGrid(rescaleIntensityButtons)))
    mainMenuButtons.append(
        ttk.Button(root, width=16, text="Morphology", command=lambda: ReplaceGrid(morphologyButtons)))

    histogramButtons.append(ttk.Button(root, width=17, text="Histogram", command=Histogram))
    histogramButtons.append(ttk.Button(root, width=17, text="Threshold", command=Threshold))
    histogramButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    filterButtons.append(ttk.Button(root, width=17, text="Prewitt", command=Prewitt))
    filterButtons.append(ttk.Button(root, width=17, text="Farid", command=Farid))
    filterButtons.append(ttk.Button(root, width=17, text="Meijering", command=Meijering))
    filterButtons.append(ttk.Button(root, width=17, text="Sato", command=Sato))
    filterButtons.append(ttk.Button(root, width=17, text="Frangi", command=Frangi))
    filterButtons.append(ttk.Button(root, width=17, text="Hessian", command=Hessian))
    filterButtons.append(ttk.Button(root, width=17, text="Gaussian", command=Gaussian))
    filterButtons.append(ttk.Button(root, width=17, text="Roberts", command=Roberts))
    filterButtons.append(ttk.Button(root, width=17, text="Sobel", command=Sobel))
    filterButtons.append(ttk.Button(root, width=17, text="Unsharp Mask", command=UnsharpMask))
    filterButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    transformButtons.append(ttk.Button(root, width=17, text="Resize", command=lambda: ReplaceGrid(resizeButtons)))
    transformButtons.append(ttk.Button(root, width=17, text="Rotate", command=Rotate))
    transformButtons.append(ttk.Button(root, width=17, text="Swirl", command=Swirl))
    transformButtons.append(ttk.Button(root, width=17, text="Rescale", command=Rescale))
    transformButtons.append(ttk.Button(root, width=17, text="Pyramid Reduce", command=PyramidReduce))
    transformButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    morphologyButtons.append(ttk.Button(root, width=17, text="Thin", command=Thin))
    morphologyButtons.append(ttk.Button(root, width=17, text="Area Opening", command=AreaOpening))
    morphologyButtons.append(ttk.Button(root, width=17, text="Area Closing", command=AreaClosing))
    morphologyButtons.append(ttk.Button(root, width=17, text="Diameter Opening", command=DiameterOpening))
    morphologyButtons.append(ttk.Button(root, width=17, text="Diameter Closing", command=DiameterClosing))
    morphologyButtons.append(ttk.Button(root, width=17, text="Erosion", command=Erosion))
    morphologyButtons.append(ttk.Button(root, width=17, text="Flood Fill", command=FloodFill))
    morphologyButtons.append(ttk.Button(root, width=17, text="Black Top Hat", command=BlackTopHat))
    morphologyButtons.append(ttk.Button(root, width=17, text="White Top Hat", command=WhiteTopHat))
    morphologyButtons.append(ttk.Button(root, width=17, text="Dilation", command=Dilation))
    morphologyButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    heightEntry = ttk.Entry(root, width=17)
    heightEntry.insert(0, "Height")
    heightEntry.bind("<FocusIn>", (lambda _: Click(heightEntry, "Height")))
    heightEntry.bind("<FocusOut>", (lambda _: Leave(heightEntry, "Height")))
    heightEntry.bind("<Unmap>", (lambda _: Unmap(heightEntry, "Height")))

    widthEntry = ttk.Entry(root, width=17)
    widthEntry.insert(0, "Width")
    widthEntry.bind("<FocusIn>", (lambda _: Click(widthEntry, "Width")))
    widthEntry.bind("<FocusOut>", (lambda _: Leave(widthEntry, "Width")))
    widthEntry.bind("<Unmap>", (lambda _: Unmap(widthEntry, "Width")))

    resizeButtons.append(heightEntry)
    resizeButtons.append(widthEntry)
    resizeButtons.append(ttk.Button(root, width=17, text="Resize",
                                    command=lambda: Resize(resizeButtons[0].get(), resizeButtons[1].get())))
    resizeButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(transformButtons)))

    angleEntry = ttk.Entry(root, width=17)
    angleEntry.insert(0, "Angle")
    angleEntry.bind("<FocusIn>", (lambda _: Click(angleEntry, "Angle")))
    angleEntry.bind("<FocusOut>", (lambda _: Leave(angleEntry, "Angle")))
    angleEntry.bind("<Unmap>", (lambda _: Unmap(angleEntry, "Angle")))
    rotateButtons.append(angleEntry)
    rotateButtons.append(ttk.Button(root, width=17, text="Rotate", command=lambda: Rotate(rotateButtons[0].get())))
    rotateButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(transformButtons)))

    for l in range(len(swirlArray)):
        if swirlArray[l] == "Rotation":
            temp = ttk.Label(root, width=15, text=swirlArray[l])
        elif swirlArray[l] == "Rotation Entry":
            temp = ttk.Entry(root, width=15)
        elif swirlArray[l] == "Strength":
            temp = ttk.Label(root, width=15, text=swirlArray[l])
        elif swirlArray[l] == "Strength Entry":
            temp = ttk.Entry(root, width=15)
        if swirlArray[l] == "Radius":
            temp = ttk.Label(root, width=15, text=swirlArray[l])
        elif swirlArray[l] == "Radius Entry":
            temp = ttk.Entry(root, width=15)
        elif swirlArray[l] == "Swirl":
            temp = ttk.Button(root, width=15, text=swirlArray[l], command=SwirlImage)
        temp.grid(column=1, row=l)
        swirlButtons.append(temp)
        temp.grid_forget()

    for m in range(len(rescaleArray)):
        if rescaleArray[m] == "Scale":
            temp = ttk.Label(root, width=15, text=rescaleArray[m])
        elif rescaleArray[m] == "Scale Entry":
            temp = ttk.Entry(root, width=15)
        elif rescaleArray[m] == "Rescale":
            temp = ttk.Button(root, width=15, text=rescaleArray[m], command=RescaleImage)
        temp.grid(column=1, row=m)
        rescaleButtons.append(temp)
        temp.grid_forget()

    for n in range(len(pyramidReduceArray)):
        if pyramidReduceArray[n] == "Downscale":
            temp = ttk.Label(root, width=15, text=pyramidReduceArray[n])
        elif pyramidReduceArray[n] == "Downscale Entry":
            temp = ttk.Entry(root, width=15)
        elif pyramidReduceArray[n] == "Pyramid Reduce":
            temp = ttk.Button(root, width=15, text=pyramidReduceArray[n], command=PyramidReduceImage)
        temp.grid(column=1, row=n)
        pyramidReduceButtons.append(temp)
        temp.grid_forget()


def MainMenu():
    for x in range(len(mainMenuButtons)):
        mainMenuButtons[x].grid(column=1, row=x)


def RescaleIntensity():
    print("Rescale Intensity")


(ttk.Button(root, text='Load Image', width=17, command=LoadImage)).place(x=160, y=450)


Construct()
MainMenu()

root.mainloop()
