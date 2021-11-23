import io
import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from skimage import data, exposure, img_as_float
from skimage import filters
from skimage.morphology import thin, area_opening, area_closing, diameter_closing, diameter_opening, erosion, \
    flood_fill, black_tophat, white_tophat, dilation
from skimage.filters import threshold_otsu
from skimage.transform import resize, rotate, swirl, rescale, pyramid_reduce
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
import cv2
import numpy as np
import threading
import imageio

root = tk.Tk()
root.iconbitmap("process.ico")  # changed icon
root.title("Image Processing")

window_width = 1000
window_height = 500

sign_image = Label(root, bg="black")
sign_image2 = Label(root, bg="black")

imageFrame = tk.Frame(root)
imageFrame2 = tk.Frame(root)
imageFrame.grid(column=0, row=0, rowspan=11, ipadx=1, ipady=1)
sign_video = tk.Label(imageFrame)
imageFrame2.grid(column=2, row=0, rowspan=11, ipadx=1, ipady=1)
sign_video2 = tk.Label(imageFrame2)

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
root.columnconfigure(0, {'minsize': (window_width / 7) * 3})
root.columnconfigure(1, {'minsize': (window_width / 7)})
root.columnconfigure(2, {'minsize': (window_width / 7) * 3})

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

mainMenuButtons = []
histogramButtons = []
filterButtons = []
transformButtons = []
morphologyButtons = []
floodFillButtons = []
rescaleIntensityButtons = []
resizeButtons = []
rotateButtons = []
swirlButtons = []
rescaleButtons = []
pyramidReduceButtons = []


def Click(entry, message):
    if (entry.get() == message):
        entry.delete(0, 'end')
    if (message == "Angle" or message == "Rotation" or message == "Strength" or message == "Radius"):
        entry.configure(validate="key", validatecommand=(entry.register(ValidationFloat), '%P'))
    elif (message == "Scale" or message == "Downscale"):
        entry.configure(validate="key", validatecommand=(entry.register(ValidationScale), '%P'))
    elif (message == "Seed Point" or message == "Input Range" or message == "Output Range"):
        entry.configure(validate="key", validatecommand=(entry.register(ValidationTuple), '%P'))
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


def ValidationScale(string):
    regex = re.compile(r"()?[0-9.]*$")
    result = regex.match(string)
    return (string == ""
            or (string.count('.') <= 1
                and result is not None
                and result.group(0) != ""))


def ValidationTuple(string):
    regex = re.compile(r"()?[0-9,]*$")
    result = regex.match(string)
    return (string == ""
            or (string.count(',') <= 1
                and result is not None
                and result.group(0) != ""))


def RenderVideo():
    if not cap.isOpened():
        return
    _, frame = cap.read()
    if not _:
        cap.release()
        out.release()
        return
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = Image.fromarray(rgb)
    img.thumbnail(((1000 / 2.40), (800 / 2.40)))
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    out.write(thresh)
    img2 = Image.fromarray(thresh)
    img2.thumbnail(((1000 / 2.40), (800 / 2.40)))
    imgtk = ImageTk.PhotoImage(image=img)
    imgtk2 = ImageTk.PhotoImage(image=img2)
    sign_video.imgtk = imgtk  # Shows frame for display 1
    sign_video.configure(image=imgtk)
    sign_video.grid(column=0, row=0, rowspan=11, ipadx=1, ipady=1)
    sign_video2.imgtk2 = imgtk2  # Shows frame for display 2
    sign_video2.configure(image=imgtk2)
    sign_video2.grid(column=2, row=0, rowspan=11, ipadx=1, ipady=1)
    root.after(10, RenderVideo)


def ProcessVideo():
    try:
        file_path = filedialog.askopenfilename(title="Select Video to Process")
        imageFrame.grid(column=0, row=0, rowspan=11, ipadx=1, ipady=1)
        imageFrame2.grid(column=2, row=0, rowspan=11, ipadx=1, ipady=1)
        sign_image.grid_forget()
        sign_image2.grid_forget()

        files = [('All files', '.*'),
                 ('AVI', '.avi')
                 ]
        time.sleep(.5)
        saveVideo = filedialog.asksaveasfile(filetypes=files, mode="w", defaultextension=".avi",
                                             title="Choose Save Location for the Processed Video")
        global cap
        cap = cv2.VideoCapture(file_path)
        width = cap.get(3)
        height = cap.get(4)
        fps = cap.get(5)

        global out
        out = cv2.VideoWriter(saveVideo.name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
                              (int(width), int(height)), False)
        RenderVideo()

        messagebox.showinfo("Success", "Video is saved at the chosen location.")

    except:
        pass


def LoadAndProcess():
    t1 = threading.Thread(target=ProcessVideo, name="Thread1")
    t1.start()


def SaveImage():
    try:
        files = [('All files', '.*'),
                 ('PNG', '.png'),
                 ('JPG', '.jpg')
                 ]
        saveFile = filedialog.asksaveasfile(filetypes=files, mode="w", defaultextension=".jpg",
                                            title="Choose Save Location for the Processed Image")
        fig.savefig(saveFile.name)
    except:
        pass


def LoadImage():
    try:
        file_path = filedialog.askopenfilename(title="Select Image to Process")
        sign_video.grid_forget()
        sign_video2.grid_forget()
        imageFrame.grid_forget()
        imageFrame2.grid_forget()
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
        sign_image2.grid(column=2, row=0, rowspan=11, columnspan=3, ipadx=1, ipady=1)

        ttk.Button(root, text='Save Image', width=17, command=SaveImage).place(x=735, y=450)
    except:
        pass


def LoadPhoto(img, h=0, w=0, type="Image", thresh=""):
    global fig
    if (h == 0 or w == 0):
        if (type == "Histogram"):
            fig = plt.Figure(figsize=(((photoWidth * 1.25) / photoWidthDpi), (photoHeight / photoHeightDpi)))
        else:
            fig = plt.Figure(figsize=((photoWidth / photoWidthDpi), (photoHeight / photoHeightDpi)))
    else:
        fig = plt.Figure(figsize=((h / photoWidthDpi), (w / photoHeightDpi)))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot()
    if (type == "Histogram"):
        ax.hist(img.ravel(), bins=256)
        ax.set_title('Histogram')
        ax.axvline(thresh, color='r')
    elif (type == "Threshold"):
        ax.imshow(img, cmap='gray')
        ax.set_title('Threshold')
    else:
        ax.imshow(img, cmap="gray")
    if (type != "Histogram"):
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        ax.axis('tight')
        ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    openedImage = Image.open(buf)
    openedImage.thumbnail((photoWidth, photoHeight))
    photo = ImageTk.PhotoImage(openedImage)
    buf.close()
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
    unsharp_mask_image = filters.unsharp_mask(image, radius=1, amount=2.0)
    LoadPhoto(unsharp_mask_image)


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


def FloodFill(seedPoint, newValue):
    seedPoint = tuple(map(int, seedPoint.split(',')))
    flood_filled_image = flood_fill(image, seed_point=(seedPoint), new_value=newValue)
    LoadPhoto(flood_filled_image)


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
    print(resized_image.shape)


def Rotate(angle):
    rotated_image = rotate(image, float(angle))
    LoadPhoto(rotated_image)


def Swirl(rotation, strength, radius):
    swirled_image = swirl(image, rotation=float(rotation), strength=float(strength), radius=float(radius))
    LoadPhoto(swirled_image)


def Rescale(scale):
    rescaled_image = rescale(image, scale=float(scale))
    LoadPhoto(rescaled_image)


def PyramidReduce(downscale):
    pyramid_reduced_image = pyramid_reduce(image, downscale=float(downscale))
    LoadPhoto(pyramid_reduced_image)


def Histogram():
    thresh = threshold_otsu(image)
    LoadPhoto(image, type="Histogram", thresh=str(thresh))


def Threshold():
    thresh = threshold_otsu(image)
    binary = image > thresh
    LoadPhoto(binary, type="Threshold")


def RescaleIntensity(inRange, outRange):
    inRange = tuple(map(int, inRange.split(',')))
    outRange = tuple(map(int, outRange.split(',')))
    rescaled_intensity = rescale_intensity(image, in_range=inRange, out_range=outRange)
    LoadPhoto(rescaled_intensity)


def ReplaceGrid(buttonArray):
    for widget in root.winfo_children():
        if (widget.winfo_class() != "Label" and widget.winfo_class() != "Frame"):
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
        ttk.Button(root, width=17, text="Rescale Intensity", command=lambda: ReplaceGrid(rescaleIntensityButtons)))
    mainMenuButtons.append(
        ttk.Button(root, width=17, text="Morphology", command=lambda: ReplaceGrid(morphologyButtons)))
    mainMenuButtons.append(ttk.Button(root, width=17, text="Video Processing", command=LoadAndProcess))

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
    transformButtons.append(ttk.Button(root, width=17, text="Rotate", command=lambda: ReplaceGrid(rotateButtons)))
    transformButtons.append(ttk.Button(root, width=17, text="Swirl", command=lambda: ReplaceGrid(swirlButtons)))
    transformButtons.append(ttk.Button(root, width=17, text="Rescale", command=lambda: ReplaceGrid(rescaleButtons)))
    transformButtons.append(
        ttk.Button(root, width=17, text="Pyramid Reduce", command=lambda: ReplaceGrid(pyramidReduceButtons)))
    transformButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    morphologyButtons.append(ttk.Button(root, width=17, text="Thin", command=Thin))
    morphologyButtons.append(ttk.Button(root, width=17, text="Area Opening", command=AreaOpening))
    morphologyButtons.append(ttk.Button(root, width=17, text="Area Closing", command=AreaClosing))
    morphologyButtons.append(ttk.Button(root, width=17, text="Diameter Opening", command=DiameterOpening))
    morphologyButtons.append(ttk.Button(root, width=17, text="Diameter Closing", command=DiameterClosing))
    morphologyButtons.append(ttk.Button(root, width=17, text="Erosion", command=Erosion))
    morphologyButtons.append(
        ttk.Button(root, width=17, text="Flood Fill", command=lambda: ReplaceGrid(floodFillButtons)))
    morphologyButtons.append(ttk.Button(root, width=17, text="Black Top Hat", command=BlackTopHat))
    morphologyButtons.append(ttk.Button(root, width=17, text="White Top Hat", command=WhiteTopHat))
    morphologyButtons.append(ttk.Button(root, width=17, text="Dilation", command=Dilation))
    morphologyButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))

    seedPointEntry = ttk.Entry(root, width=17)
    seedPointEntry.insert(0, "Seed Point")
    seedPointEntry.bind("<FocusIn>", (lambda _: Click(seedPointEntry, "Seed Point")))
    seedPointEntry.bind("<FocusOut>", (lambda _: Leave(seedPointEntry, "Seed Point")))
    seedPointEntry.bind("<Unmap>", (lambda _: Unmap(seedPointEntry, "Seed Point")))

    newValueEntry = ttk.Entry(root, width=17)
    newValueEntry.insert(0, "New Value")
    newValueEntry.bind("<FocusIn>", (lambda _: Click(newValueEntry, "New Value")))
    newValueEntry.bind("<FocusOut>", (lambda _: Leave(newValueEntry, "New Value")))
    newValueEntry.bind("<Unmap>", (lambda _: Unmap(newValueEntry, "New Value")))

    floodFillButtons.append(seedPointEntry)
    floodFillButtons.append(newValueEntry)
    floodFillButtons.append(ttk.Button(root, width=17, text="Flood Fill",
                                       command=lambda: FloodFill(floodFillButtons[0].get(), floodFillButtons[1].get())))
    floodFillButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(morphologyButtons)))

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

    rotationEntry = ttk.Entry(root, width=17)
    rotationEntry.insert(0, "Rotation")
    rotationEntry.bind("<FocusIn>", (lambda _: Click(rotationEntry, "Rotation")))
    rotationEntry.bind("<FocusOut>", (lambda _: Leave(rotationEntry, "Rotation")))
    rotationEntry.bind("<Unmap>", (lambda _: Unmap(rotationEntry, "Rotation")))

    strengthEntry = ttk.Entry(root, width=17)
    strengthEntry.insert(0, "Strength")
    strengthEntry.bind("<FocusIn>", (lambda _: Click(strengthEntry, "Strength")))
    strengthEntry.bind("<FocusOut>", (lambda _: Leave(strengthEntry, "Strength")))
    strengthEntry.bind("<Unmap>", (lambda _: Unmap(strengthEntry, "Strength")))

    radiusEntry = ttk.Entry(root, width=17)
    radiusEntry.insert(0, "Radius")
    radiusEntry.bind("<FocusIn>", (lambda _: Click(radiusEntry, "Radius")))
    radiusEntry.bind("<FocusOut>", (lambda _: Leave(radiusEntry, "Radius")))
    radiusEntry.bind("<Unmap>", (lambda _: Unmap(radiusEntry, "Radius")))

    swirlButtons.append(rotationEntry)
    swirlButtons.append(strengthEntry)
    swirlButtons.append(radiusEntry)
    swirlButtons.append(ttk.Button(root, width=17, text="Swirl",
                                   command=lambda: Swirl(swirlButtons[0].get(), swirlButtons[1].get(),
                                                         swirlButtons[2].get())))
    swirlButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(transformButtons)))

    scaleEntry = ttk.Entry(root, width=17)
    scaleEntry.insert(0, "Scale")
    scaleEntry.bind("<FocusIn>", (lambda _: Click(scaleEntry, "Scale")))
    scaleEntry.bind("<FocusOut>", (lambda _: Leave(scaleEntry, "Scale")))
    scaleEntry.bind("<Unmap>", (lambda _: Unmap(scaleEntry, "Scale")))

    rescaleButtons.append(scaleEntry)
    rescaleButtons.append(ttk.Button(root, width=17, text="Rescale", command=lambda: Rescale(rescaleButtons[0].get())))
    rescaleButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(transformButtons)))

    downscaleEntry = ttk.Entry(root, width=17)
    downscaleEntry.insert(0, "Downscale")
    downscaleEntry.bind("<FocusIn>", (lambda _: Click(downscaleEntry, "Downscale")))
    downscaleEntry.bind("<FocusOut>", (lambda _: Leave(downscaleEntry, "Downscale")))
    downscaleEntry.bind("<Unmap>", (lambda _: Unmap(downscaleEntry, "Downscale")))

    pyramidReduceButtons.append(downscaleEntry)
    pyramidReduceButtons.append(
        ttk.Button(root, width=17, text="Pyramid Reduce", command=lambda: PyramidReduce(pyramidReduceButtons[0].get())))
    pyramidReduceButtons.append(ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(transformButtons)))

    inRangeEntry = ttk.Entry(root, width=17)
    inRangeEntry.insert(0, "Input Range")
    inRangeEntry.bind("<FocusIn>", (lambda _: Click(inRangeEntry, "Input Range")))
    inRangeEntry.bind("<FocusOut>", (lambda _: Leave(inRangeEntry, "Input Range")))
    inRangeEntry.bind("<Unmap>", (lambda _: Unmap(inRangeEntry, "Input Range")))

    outRangeEntry = ttk.Entry(root, width=17)
    outRangeEntry.insert(0, "Output Range")
    outRangeEntry.bind("<FocusIn>", (lambda _: Click(outRangeEntry, "Output Range")))
    outRangeEntry.bind("<FocusOut>", (lambda _: Leave(outRangeEntry, "Output Range")))
    outRangeEntry.bind("<Unmap>", (lambda _: Unmap(outRangeEntry, "Output Range")))

    rescaleIntensityButtons.append(inRangeEntry)
    rescaleIntensityButtons.append(outRangeEntry)
    rescaleIntensityButtons.append(ttk.Button(root, width=17, text="Rescale Intensity",
                                              command=lambda: RescaleIntensity(rescaleIntensityButtons[0].get(),
                                                                               rescaleIntensityButtons[1].get())))
    rescaleIntensityButtons.append(
        ttk.Button(root, width=17, text="Back", command=lambda: ReplaceGrid(mainMenuButtons)))


def MainMenu():
    for x in range(len(mainMenuButtons)):
        mainMenuButtons[x].grid(column=1, row=x)


(ttk.Button(root, text='Load Image', width=17, command=LoadImage)).place(x=160, y=450)

Construct()
MainMenu()

root.mainloop()
