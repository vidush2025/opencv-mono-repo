import cv2;
image = cv2.imread("testmedia\joeGoldberg.jpg")

if image is not None:
    len, bre, col = image.shape #length, bredth, colour channels
    print("Image Loaded")
    print("Length:", len, "Breadth:", bre)
    print("Colour Channels:", col)
else:
    print("Could  not load image.")