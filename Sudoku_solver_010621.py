'''
#Created by: Jack Cornwall
#Email: jackcornwall91@gmail.com
#Git hub: https://github.com/JackDCornwall
#Website:https://jackcornwall.co.uk/

#Project: Sudoku solver
#Date: 010621
#Description: Upload an image of a sudoku, centre it in the square and boom it will be solved for you.
'''

#importing required directories
import os
import cv2
import pytesseract
import numpy as np

#directories and path
dir = os.getcwd() #working directory
ocr_tesseract_path = "C://Users/Jack/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
img_dir = dir + "\\Resources\\" #image/resource directory
#path = img_dir + "Sudoku_0.jpg"
path = img_dir + "Sudoku_5.png"

#print(os.listdir(img_dir)) #printing sudoku files

#importing image
img = cv2.imread(path)
imgOut = img.copy() #creating a copy to draw on

#converting image to greyscale and adding blur
imgGrey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGrey,(7,7),1)
#imgBlur = imgGrey

#finding edges with Canny function
imgCanny = cv2.Canny(imgBlur,100,100)

#extracting contour coordinates & hierarchy (hierarchy not necessary)
#contours,hierarchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) #only external most contour returned
contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)

#initialising an array to store areas
areas = []

#calculating all areas
for cnt in contours:

    #calculating area
    areas.append(cv2.contourArea(cnt))

#extracting largest area
max_area = max(areas)

# #TODO code below looks at finding second largest area and seeing if it is a sudoku contained in a box
# #Sudoku_0.jpg should trigger this but does not, only one contour is being returned.
# #I have asked for help in discord
# max_area_2 = 0
# if len(areas) > 1:
#
#     #looping through all areas
#     for a in areas:
#
#         #checking for second largest number
#         #also attempts to remove (areas that are virtually identical to max_area, double overlapping contours)
#         if a < (max_area-(max_area*0.1)) and a > max_area_2:
#
#             max_area_2 = a
#             print(max_area_2)
#
#     #moving to inner box if its smaller
#     if (max_area_2/max_area) > 0.5:
#
#          print("Sudoku found inside box?") #notification message
#
# print(max_area)
# #print(max_area_2)

#extracting height & width of the imported image
heightOld = imgCanny.shape[0]
widthOld = imgCanny.shape[1]

#Calculating area
imgArea = heightOld * widthOld

#TODO re-enable when appropriate
# if (max_area/imgArea) < 0.3:
#     print("Sudoku not captured correctly")
#     print("Take a closer picture of the sudoku")
#     print("or make sure the entire outer border is visible.")
#     print("Ratio of sudoku to image:",max_area/imgArea)
#     print("For image:",path)

contour = contours[areas.index(max_area)]

#print(len(contour))

#TODO re-enable when appropriate
#checking only 4 corners are found
# if len(corners)!=4:
#
#     #printing error message
#     print("Sudoku does not have 4 corners")

#drawing contour
cv2.drawContours(imgOut,contour,-1,(125,0,225),2)

#TODO check that ratio between width and height is roughly square

# calculating perimeter
perimeter = cv2.arcLength(contour, True)

# approximate corner points (should always be 4 for a box)
corners = cv2.approxPolyDP(contour, 0.02*perimeter, True)

#defining old points in the following order:
# 1.top left
# 2.top right
# 3.bottom left
# 4.bottom right
ptsOld = np.float32([corners[0],corners[3],corners[1],corners[2]])

#height and width of exported sudoku
widthNew = 512
heightNew = 512

# points to transform to on new image in the following order:
# 1.top left
# 2.top right
# 3.bottom left
# 4.bottom right
ptsNew = np.float32([[0, 0], [widthNew, 0], [0, heightNew], [widthNew, heightNew]])

# generatin transformation matrix
matrix = cv2.getPerspectiveTransform(ptsOld, ptsNew)

# transforming image (performing warp)
imgWarp = cv2.warpPerspective(img, matrix, (widthNew, heightNew))

#subdividing and extracting digits in cells

#pointing to ocr tessearact instasll
pytesseract.pytesseract.tesseract_cmd = ocr_tesseract_path


#calculating dimensions of cells
widthCell = round(widthNew/9)
heightCell = round(heightNew/9)

#creating np array
sudoku = np.zeros(shape=(9,9),dtype=int)

#configurations for tesseract
#oem 3 is the default tessearct engine
#psm 10 expects to detect a single caracter
#outputbase digits means we are looking for digits
conf = r"--oem 3 --psm 10 outputbase digits"

#reading from left to right
#looping through cols
for col in range(0,9):

    #looping throuhg rows
    for row in range(0,9):

        #cropping cell image

        #dimensions to crop (shrunk slightly to avoid borders)
        width_start = (widthCell * row) + 10
        width_end = (widthCell * row + widthCell) - 10
        height_start = (heightCell * col) + 10
        height_end = (heightCell * col + heightCell) - 10

        #defiing cell outline as follows: imgCell[y:y+h,x:x+w]
        imgCell = imgWarp[height_start : height_end , width_start : width_end]

        #converting to RGB from BGR as needed by pytesseract
        imgRGB = cv2.cvtColor(imgCell,cv2.COLOR_BGR2GRAY)

        digit = pytesseract.image_to_string(imgRGB,config=conf)  #detect & extract digit

        #TODO sub \x0c and \n from digit and then make sure only alphanumeric values are present

        #storing extracted digit
        #sudoku[row][col] = int(digit)

        print(digit)
        #print(type(digit))

        #cv2.imshow("Grid cell",imgCell)
        #cv2.waitKey(1000)

#outputting image
cv2.imshow("Detected Sudoku",imgOut)
cv2.imshow("Isolated Sudoku", imgWarp)

cv2.waitKey(0) #indefinite delay

print("Code run successfully")