import cv2
from darkflow.net.build import TFNet
import matplotlib.pyplot as plt 

options = {
	'model': 'cfg/tiny-yolo-voc-1c.cfg',
	'load': 1125,
	'threshold': 0.1
}

tfnet = TFNet(options)

img = cv2.imread('sample_img/NumberPlate4.jpg', cv2.IMREAD_COLOR)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
result = tfnet.return_predict(img)

tl = (result[0]['topleft']['x'], result[0]['topleft']['y'])
br = (result[0]['bottomright']['x'], result[0]['bottomright']['y'])
label = result[0]['label']
confidence = result[0]['confidence']

img = cv2.rectangle(img, tl, br, (0,255,0), 7)
img = cv2.putText(img, label, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)
img = cv2.putText(img, str(confidence), br, cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,0), 2)

x1,y1 = tl
x2,y2 = br
license_plate = img[y1:y2, x1:x2]

plt.imshow(img)
plt.show()

plt.imshow(license_plate)
plt.show()