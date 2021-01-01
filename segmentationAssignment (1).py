"""
Segmentation

Performance ->  Program works for an array of different images depends on the size of the radius in the program itself, 
                configured for the test images. radius 13-50.  For the 3 test images the code works equally well,
                though the golf picture due to the makeup for grass is more obvious then the others at the end inpainting it in. 
                Program runs quickly on all images less then .2 seconds on my machine so performs quicker incomparison to other methods
                where it returns alot more circles and has to iterate them      

Other Test Images ->  minRadius to maxRadius radius: 108- > 170 https://img.pixers.pics/pho_wat(s3:700/FO/35/74/41/45/700_FO35744145_cb200cd3bd7627d8ba93aaa2b2d26436.jpg,700,700,cms:2018/10/5bd1b6b8d04b8_220x50-watermark.png,over,480,650,jpg)/wall-murals-black-and-white-soccer-ball-on-grass.jpg.jpg
                      minRadius to maxRadius radius: 200 -> 400 https://c8.alamy.com/comp/F7R6CF/white-soccer-ball-on-grass-at-goal-and-stadium-in-background-F7R6CF.jpg
                      Works on an Array of other images, just change the minRadius + maxRadius, 
                      didnt include changing it in the program as its too complicated for users to decide the right distances....
 
Research -> Research into open cv included HoughCircles which are used to determine circles in an image by radius, looked into eliminating false postitives
            InPainting -> created a mask using the circles detected of white balls and fill it in off the edited image
            Detecting color based on upper and lower ranges to determine if the ball is white
            Creating a mask based on range values for the color white, however this picked up too much noise based on reflection of light
                on the grass            

General comment on how it works ->  Reads in an image and converts it to grayscale, it then uses houghcircles to detect circles within the image
                                    it then iterates through these circles, to determine if they are somewhat white in color, i took the B from RGB and determined
                                    it was above 140, as this in general yielded only white balls when tested on other images, it then draws a white circle 
                                    slightly larger then the ball detected.  it then grabs the outer edges of this and inpaints it, which gives a blur but
                                    obscured result which works great for fake grass, and snooker tables etc


Pseudo Description of Algoritim:
    1) Gets Image from file
    2) Converts the image to GrayScale
    3) Blurs the image and returns it
    4) Detects the circles within the specified parameters based on the grayscale image 
    5) Checks that there are circles which exist
    6) Iterates through the circles
    7) takes the center of the circle detected
    8) takes the height width or the Image
    9) checks if the circles are actually within the image itself ie eliminate false circles on the edges
    10) checks that the circle center pixel is above 120 to detemine if its some shade of white
    11) draws a white circle thats infilled white that add 15 to the radius, (this eliminates some shadows when filling it back in later)
    12) if no white-ish color is detected, out put it to the user and end program
    13) if balls in general are detected output to the user and end program
    14) Gets the grayscale of the image without a blur
    15) gets the threshold of this image -> The ball has been replaced with a white circle in this image
    16) The original picture and the mask is placed into an infill function which takes the outer pixels of the white circles and infills them back
        onto the origional image   
    17) program ends

"""
import sys
import cv2
import numpy as np
import easygui

def getImage():
    file_ = easygui.fileopenbox()
    Image = cv2.imread(file_)
    return Image

def getColorChannel(Image):
    Gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY) 
    # 7 produced the optimum output for all images
    Gray = cv2.medianBlur(Gray, 7)   
    return Gray

    # Color channel with no blur returns a better result then using the same getColorChannel
def getColorChannelNoBlur(Image):
    Gray = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY) 
    return Gray

def getCircles(gray):
    # just height value of Image
    rows = gray.shape[0]
    # Detection of false circles by choosing circles within these parameters were optimised for test images, 
    # but work on balls with similar radius on other pictures
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 20,param1=125, param2=28,minRadius=13, maxRadius=50)
    return circles

def drawCircles(Image,circles):
    # checks if any circles had been detected
    # Error checking
    if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                center = (i[0], i[1])
                height, width, channels = Image.shape
                # Checks circles centers exist on the Image
                if i[0] < height and i[1] < width:
                    # checks if the color is over this range to detect white-ish objects, just checking 1 range as the others varied too greatly to count ie, [70,150,2]
                    if Image[center][1] > 140:
                            # circle outline
                            radius = i[2]
                            # Adds 15 to the radius to prevent a dark shadow from mixing when in filling later as well as not
                            # not getting the out circle outline in some cases
                            cv2.circle(Image, center, radius+15, (255, 255, 255), -1)
    else:
        easygui.msgbox("No balls detected in the image, Program Ending")
        exit()              
    return Image

def getThreshold(G):
    # global thresholding
    ret1,th1 = cv2.threshold(G, 240,255,cv2.THRESH_BINARY)
    return th1

def repaintImage(Image, threshold):
    # 2 is selected here as it yields the best blurred result
    Image = cv2.inpaint(Image,threshold,2,cv2.INPAINT_TELEA)
    return Image

def showImage(Image):
    cv2.imshow("detected circles",  Image)
    cv2.waitKey(0)
    
def main(argv):
    Image = getImage() 
    GrayScale = getColorChannel(Image)
    Circles=getCircles(GrayScale)
    Image = drawCircles(Image,Circles)
    GrayScaleNoBlur = getColorChannelNoBlur(Image)
    Threshold = getThreshold(GrayScaleNoBlur)
    Image = repaintImage(Image, Threshold)
    showImage(Image)
    exit()
    
if __name__ == "__main__":
    main(sys.argv[1:])
