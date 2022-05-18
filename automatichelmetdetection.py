# fairviewimport cv2
import datetime
import numpy as np
import os

import DetectChars
import DetectPlates
import PossiblePlate

# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)

SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

likplates=""

###################################################################################################
def main(k):

    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()         # attempt KNN training

    if blnKNNTrainingSuccessful == False:                               # if KNN training was not successful
        print("\nerror: KNN traning was not successful\n")  # show error message
        return                                                          # and exit program
    # end if
    print("Path   ",k)
    imgOriginalScene  = cv2.imread(k)               # open image

    if imgOriginalScene is None:                            # if image was not read successfully
        print("\nerror: image not read from file \n\n")  # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                              # and exit program
    # end if

    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates

    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    cv2.imshow("imgOriginalScene", imgOriginalScene)            # show scene image

    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        print("\nno license plates were detected\n")  # inform user no plates were found
    else:                                                       # else
                # if we get in here list of possible plates has at leat one plate

                # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)

                # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate




        licPlate = listOfPossiblePlates[0]

        print("Lic  ",licPlate)




        # cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
        # cv2.imshow("imgThresh", licPlate.imgThresh)

        if len(licPlate.strChars) == 0:                     # if no chars were found in the plate
            print("\nno characters were detected\n\n")  # show message
            return                                          # and exit program
        # end if

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)             # draw red rectangle around plate

        print("\nlicense plate read from image = " + licPlate.strChars + "\n")  # write license plate text to std out
        print("----------------------------------------")

        writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)           # write license plate text on the image

        # cv2.imshow("imgOriginalScene", imgOriginalScene)                # re-show scene image
        lic_no=str(licPlate.strChars).replace("I","1").replace("S","5")
        print("hloooo  ",licPlate.strChars, lic_no)
        import re
        for veh_no in nmbr_plates:
            if lic_no in veh_no:
                print("Recognized..  Violator number : "+veh_no)
                db=Db()
                res=db.selectOne("select * from  vehicle where v_no='"+veh_no+"'")
                if res is not None:
                    v_id=res['v_id']
                    res1=db.selectOne("select * from helmet where v_id='"+str(v_id)+"' and date=curdate()")
                    if res1 is None:
                        dt=time.strftime("%Y%m%d_%H%M%S")
                        cv2.imwrite("C:\\Users\\TUF GAMING\\PycharmProjects\\GLIMPSE\\static\\helmetpic\\"+dt+".jpg", imgOriginalScene)
                        pth="/static/helmetpic/"+dt+".jpg"
                        db.insert("insert into helmet(v_id, date, image, p_status) values('"+str(v_id)+"',curdate(),'"+pth+"','pending')")


        # cv2.imwrite("imgOriginalScene.png", imgOriginalScene)           # write image out to file

    # end if else

    # cv2.waitKey(0)					# hold windows open until user presses a key

    return
# end main

###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect
    # print("hiii   ", p2fRectPoints)
    # print("hiiiii   ", tuple(p2fRectPoints[0]))

    p1=tuple([int(tuple(p2fRectPoints[0])[0]), int(tuple(p2fRectPoints[0])[1])])

    p2=tuple([int(tuple(p2fRectPoints[1])[0]), int(tuple(p2fRectPoints[1])[1])])
    p3=tuple([int(tuple(p2fRectPoints[2])[0]), int(tuple(p2fRectPoints[2])[1])])
    p4=tuple([int(tuple(p2fRectPoints[3])[0]), int(tuple(p2fRectPoints[3])[1])])

    print(p1, p2, p3, p4)

    try:
        cv2.line(imgOriginalScene, p1, p2, SCALAR_RED, 2)         # draw 4 red lines
        cv2.line(imgOriginalScene, p2, p3, SCALAR_RED, 2)
        cv2.line(imgOriginalScene, p3, p4, SCALAR_RED, 2)
        cv2.line(imgOriginalScene, p4, p1, SCALAR_RED, 2)
    except Exception as e:
        print("Errrr   ", e)
# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

            # write the text on the image
    # cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function





from skimage.io import imread
from skimage.filters import threshold_otsu
import matplotlib.pyplot as plt
import cv2
from skimage import measure
from skimage.measure import regionprops

def licenseplatedetection(a,i):
    (startX, startY, endX, endY)=i
    print(i,"aaaaaaaaaaaaaaaaa")





    car_image = imread(a, as_gray=True)

    print(startX,startY,endX,endY,"hoooooo")


    gray_car_image = car_image * 255
    print("1")
    threshold_value = threshold_otsu(gray_car_image)
    binary_car_image = gray_car_image > threshold_value
    m = 0
    label_image = measure.label(binary_car_image)
    plate_dimensions = (
    0.03 * label_image.shape[0], 0.08 * label_image.shape[0], 0.15 * label_image.shape[1], 0.3 * label_image.shape[1])
    plate_dimensions2 = (
    0.08 * label_image.shape[0], 0.2 * label_image.shape[0], 0.15 * label_image.shape[1], 0.4 * label_image.shape[1])
    min_height, max_height, min_width, max_width = plate_dimensions
    plate_objects_cordinates = []
    plate_like_objects = []
    flag = 0

    # regionprops creates a list of properties of all the labelled regions

    for region in regionprops(label_image):
        if region.area < 50:
            continue
        min_row, min_col, max_row, max_col = region.bbox
        region_height = max_row - min_row
        region_width = max_col - min_col
        if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
            flag = 1
            plate_like_objects.append(binary_car_image[min_row:max_row, min_col:max_col])
            plate_objects_cordinates.append((min_row, min_col, max_row, max_col))
            car_image = cv2.imread(a)
            ss = car_image[min_row: min_row + (max_row - min_row), min_col: min_col + (max_col - min_col)]
            print(min_col, min_row, max_col, max_row)
            print(type(ss))
            cv2.imwrite(str(m) + ".jpg", ss)
            m = m + 1








# import necessary packages
from imutils.video import VideoStream
import numpy as np
from imutils.video import FPS
import imutils
import time
import cv2
from keras.models import load_model
from DBConnection import Db

# initialize the list of class labels MobileNet SSD was trained to detect
# generate a set of bounding box colors for each class
CLASSES = ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
#CLASSES = ['motorbike', 'person']
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

print('Loading helmet model...')
loaded_model = load_model('new_helmet_model.h5')
loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# initialize the video stream,
print("[INFO] starting video stream...")


# nmbr_plates=['KL11Z8536', 'KL11BJ8875', 'KL52B8581', 'KL13AG392', 'KL13AR3859', 'KL13AJ1028', 'KL59J3151', 'KL13AJ4753']
nmbr_plates=[]
db=Db()
rr=db.select("select * from vehicle")
for i in rr:
    nmbr_plates.append(i['v_no'])
print("Number plates  ", nmbr_plates)

# Loading the video file
# cap = cv2.VideoCapture('vid1.mp4')
cap = cv2.VideoCapture("solo_nohelmet2.mp4")

# time.sleep(2.0)

# Starting the FPS calculation
fps = FPS().start()

# loop over the frames from the video stream
# i = True
while True:
    # i = not i
    # if i==True:

    try:
        # grab the frame from the threaded video stream and resize it
        # to have a maxm width and height of 600 pixels
        ret, frame = cap.read()

        frame1=frame

        # resizing the images
        # frame = imutils.resize(frame, width=600, height=600)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        
        # Resizing to a fixed 300x300 pixels and normalizing it.
        # Creating the blob from image to give input to the Caffe Model
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)

        detections = net.forward()  # getting the detections from the network
        
        persons = []
        person_roi = []
        motorbi = []
        
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence associated with the prediction
            confidence = detections[0, 0, i, 2]
            
            # filter out weak detections by ensuring the confidence
            # is greater than minimum confidence
            if confidence > 0.5:
                
                # extract index of class label from the detections
                idx = int(detections[0, 0, i, 1])
                
                if idx == 15:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    # roi = box[startX:endX, startY:endY/4] 
                    # person_roi.append(roi)
                    persons.append((startX, startY, endX, endY))

                if idx == 14:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    motorbi.append((startX, startY, endX, endY))

        xsdiff = 0
        xediff = 0
        ysdiff = 0
        yediff = 0
        p = ()
        
        for i in motorbi:
            mi = float("Inf")
            for j in range(len(persons)):
                xsdiff = abs(i[0] - persons[j][0])
                xediff = abs(i[2] - persons[j][2])
                ysdiff = abs(i[1] - persons[j][1])
                yediff = abs(i[3] - persons[j][3])

                if (xsdiff+xediff+ysdiff+yediff) < mi:
                    mi = xsdiff+xediff+ysdiff+yediff
                    p = persons[j]
                    # r = person_roi[j]


            if len(p) != 0:

                # display the prediction
                label = "{}".format(CLASSES[14])                            ##########33            motorbike
                # print("[INFO] {}".format(label))
                cv2.rectangle(frame, (i[0], i[1]), (i[2], i[3]), COLORS[14], 2)
                y = i[1] - 15 if i[1] - 15 > 15 else i[1] + 15
                cv2.putText(frame, label, (i[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[14], 2)
                label = "{}".format(CLASSES[15])                            #######             person
                # print("[INFO] {}".format(label))

                cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), COLORS[15], 2)
                y = p[1] - 15 if p[1] - 15 > 15 else p[1] + 15

                roi = frame[p[1]:p[1]+(p[3]-p[1])//4, p[0]:p[2]]
                # print(roi)

                if len(roi) != 0:
                    img_array = cv2.resize(roi, (50,50))
                    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    img = np.array(gray_img).reshape(1, 50, 50, 1)
                    img = img/255.0
                    prediction = loaded_model.predict_proba([img])

                    print("PPP   ",prediction[0][0])

                    cv2.rectangle(frame, (p[0], p[1]), (p[0] + (p[2] - p[0]), p[1] + (p[3] - p[1]) // 4), COLORS[0], 2)
                    cv2.putText(frame, str(round(prediction[0][0], 2)), (p[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                COLORS[0], 2)

                    if prediction[0][0] > 0.9:                          ##########################              threshold
                        timestr = time.strftime("%Y%m%d-%H%M%S")

                        try:

                            filename = timestr + "frame.jpg"
                            # cv2.imwrite("D:\\backups\\Mes KTPRM\\Helmet\\HelmetViolator\\HelmetViolator\\static\\helmet_images\\"+filename, frame)
                            #
                            # (startX, startY, endX, endY) = i
                            # print(i, "aaaaaaaaaaaaaaaaa")
                            #
                            # car_image = imread("D:\\backups\\Mes KTPRM\\Helmet\\HelmetViolator\\HelmetViolator\\static\\helmet_images\\"+filename, as_gray=True)
                            #
                            # print(startX, startY, endX, endY, "hoooooo")

                            kd = frame[ startY:endY,startX:endX]

                            cv2.imwrite("D:\\a.jpg", kd)
                            k=main("D:\\a.jpg")

                            # cv2.imwrite("D:\\a.jpg"+filename, kd)
                            # k=main("D:\\a.jpg"+filename)

                            # print(i,"aaaaaaaaaaaa")
                            #
                            #
                            #
                            # db = Db()
                            #
                            # licenseplatedetection("D:\\"+filename,i)
                            # print("Before")
                            # licenseplatedetection("D:\\a.jpg", i)
                            # db.insert("INSERT INTO `helmet_violation` VALUES(NULL,1,'"+filename+"',CURDATE(),CURTIME(),str(k))")

                            cv2.imwrite(timestr+"frame.jpg", frame)  # save frame as JPEG file
                        except Exception as e:
                            print(e)








    except:
        pass

    # cv2.imshow('Frame', frame)  # Displaying the frame
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'): # if 'q' key is pressed, break from the loop
        break
     
    # update the FPS counter
    fps.update()


# stop the timer and display FPS information
fps.stop()

print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
 
cv2.destroyAllWindows()
cap.release()   # Closing the video stream 









