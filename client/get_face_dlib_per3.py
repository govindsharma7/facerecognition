# -*- coding:utf-8 -*-
import cv2
import datetime
import dlib
import os
import json
import requests
import time
import sys
import random
from align_dlib import AlignDlib
from scipy.misc import imsave

from sftp_upload import sftp_upload

output_dir = '/Users/Lavector/git-back/facerecognition/client/my_faces'
size = 160

host = '121.69.75.194'  # 主机
port = 22  # 端口
username = 'wac'  # 用户名
password = '8112whz'  # 密码
local = '/Users/ngxin/facerecognition/client/face_recognition/my_faces'
remote = '/home/wac/ngxin/ftp_upload/'


face_predictor_path = './model/shape_predictor_68_face_landmarks.dat'
align = AlignDlib(face_predictor_path)
landmarkIndices = AlignDlib.OUTER_EYES_AND_NOSE

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
#获取mac地址

def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return mac

detector = dlib.get_frontal_face_detector()
camera = cv2.VideoCapture(0)
index = 1
while True:

    print('Being processed picture %s' % index)
    frame, img = camera.read()
    cv2.imshow('face', img)
    if (index % 10 == 0):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        dets = detector(gray_img)

        for i, d in enumerate(dets):
            add = 80

            x1 = d.left() - add
            x2 = d.right() + add
            y1 = d.top() - add
            y2 = d.bottom() + add
            x1 = x1 if x1 > 0 else 0
            x2 = x2 if x2 < gray_img.shape[1] else gray_img.shape[1]
            y1 = y1 if y1 > 0 else 0
            y2 = y2 if y2 < gray_img.shape[0] else gray_img.shape[0]


            face = img[y1:y2, x1:x2]
            face = cv2.resize(face, (size,size))

            # align face pose
            aligned = align.align(160, face, [0, 0, size, size], landmarkIndices=landmarkIndices)
            aligned = cv2.resize(aligned, (size, size))


            cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            mac_addr = get_mac_address()
            path_init = output_dir + '/' + mac_addr + cur_time+str(index) + str(i) + '.jpg'
            path_aligned = output_dir + '/' + mac_addr + cur_time + str(index) + str(i) + '_init.jpg'
            cv2.imwrite(path_init, aligned)
            cv2.imwrite(path_aligned, img[d.top():d.bottom(), d.left():d.right()])
            #sftp_upload(host, port, username, password, local, remote)


            message_search = {"id": "weibo",
                              "pics": [{
                                           "path": path_init,
                                           "path_aligned": path_aligned,
                                           "id": cur_time, "consume_history": "True"}]
                              }
            temp = json.dumps(message_search)
            payloadfiles = {'files': temp}

            start = time.time()
            r = requests.post("http://0.0.0.0:3006/query", data=payloadfiles)
            result = json.loads(r.text)
            if result['result'] != 'error':
                text = result['tag'][cur_time]
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, text, (x1, y1), font, 3, (0, 255, 255), 2)
            rect = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.imshow('face', img)
            print time.time() - start
            print r.text
    index += 1

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
