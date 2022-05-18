# import necessary packages
from imutils.video import VideoStream
import numpy as np
from imutils.video import FPS
import imutils
import time

from keras.models import load_model
import cv2
from DBConnection import Db
import os

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

# Loading the video file
cap = cv2.VideoCapture('sreerag.mp4')
# cap = cv2.VideoCapture('v.mp4')

# time.sleep(2.0)

# Starting the FPS calculation
fps = FPS().start()

# loop over the frames from the video stream
# i = True
while True:
    # print("")
    # i = not i
    # if i==True:

    try:
        # grab the frame from the threaded video stream and resize it
        # to have a maxm width and height of 600 pixels
        ret, frame = cap.read()

        # resizing the images
        frame = imutils.resize(frame, width=300, height=300)
        cv2.imwrite("pic.jpg", frame)

        import datetime
        date = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        path = '/static/triple_pic/'+date+'.jpg'
        cv2.imwrite(r"C:\Users\TUF GAMING\PycharmProjects\GLIMPSE\static\triple_pic\\"+date+".jpg", frame)
        fr=cv2.imread("triples_yes.jpeg")
        frame=fr.resize(600, 600)


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

        print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence associated with the prediction
            confidence = detections[0, 0, i, 2]


            # filter out weak detections by ensuring the confidence
            # is greater than minimum confidence
            if confidence > 0.5:
                print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")

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
                label = "{}".format(CLASSES[14])
                print("aaaaa",label)


                print("[INFO] {}".format(label))
                cv2.rectangle(frame, (i[0], i[1]), (i[2], i[3]), COLORS[14], 2)
                y = i[1] - 15 if i[1] - 15 > 15 else i[1] + 15
                cv2.putText(frame, label, (i[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[14], 2)
                label = "{}".format(CLASSES[15])
                print("[INFO] {}".format(label))

                cv2.rectangle(frame, (p[0], p[1]), (p[2], p[3]), COLORS[15], 2)
                y = p[1] - 15 if p[1] - 15 > 15 else p[1] + 15

                roi = frame[p[1]:p[1]+(p[3]-p[1])//4, p[0]:p[2]]

                print("hellllllllllllllooooooooooo")
                print(len(roi))

                if len(roi) != 0:
                    img_array = cv2.resize(roi, (50,50))
                    gray_img = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    img = np.array(gray_img).reshape(1, 50, 50, 1)

                    img = img/255.0

                    # prediction = loaded_model.predict_proba([img])
                    prediction = loaded_model.predict([img])

                    print("hiiiiiii")
                    print("PPPP   ",prediction)

                    timestr = time.strftime("%Y%m%d-%H%M%S")


                    if prediction[0][0] >0.7:
                        try:
                            filename = timestr+"frame.jpg"
                            print(filename)

                            # triples code

                            # cv2.imwrite("C:\\Users\\HP\\PycharmProjects\\HelmetViolator\\static\\helmet_images\\"+filename, frame)
                            cv2.imwrite(r"C:\Users\TUF GAMING\PycharmProjects\GLIMPSE\static\helmetpic\\"+filename, frame)
                            path="/static/helmetpic/"+filename
                            db = Db()
                            # db.insert("INSERT INTO helmet_violation VALUES(NULL,1,CURDATE(),CURTIME(),'"+str(path)+"','pending')")
                            print("violation")
                            db.insert("insert into triples(image, date, p_status) values('"+path+"', curdate(), 'pending')")
                            cv2.imwrite(timestr+"frame.jpg", frame)  # save frame as JPEG file

                            # time.sleep(60)

                        except Exception as e:
                            print(e)


                        cv2.rectangle(frame, (p[0], p[1]), (p[0]+(p[2]-p[0]), p[1]+(p[3]-p[1])//4), COLORS[0], 2)
                        cv2.putText(frame, str(round(prediction[0][0],2)), (p[0], y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[0], 2)




    except:
        pass

    cv2.imshow('Frame', frame)  # Displaying the frame
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

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

# image_path = sys.argv[1]
# image_path="C:\\Users\\ELCOT-Lenovo\\Documents\\images\\sign_dataset\\test\\A\\color_0_0016"
# Read the image_data
image_data = tf.gfile.FastGFile("pic.jpg", 'rb').read()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line
               in tf.gfile.GFile("C:/Users/TUF GAMING/PycharmProjects/GLIMPSE/logs/output_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("C:/Users/TUF GAMING/PycharmProjects/GLIMPSE/logs/output_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

with tf.Session() as sess:
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    predictions = sess.run(softmax_tensor, \
                           {'DecodeJpeg/contents:0': image_data})

    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    for node_id in top_k:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        print('%s (score = %.5f)' % (human_string, score))

        if human_string == 'triple':
            db = Db()
            db.insert("insert into triples (image,date,p_status) values ('"+str(path)+"',curdate(),'violated')")

