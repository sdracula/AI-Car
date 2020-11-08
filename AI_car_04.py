import requests 
from aip import AipFace
import cv2
import base64
import numpy
import time
import os
import v4l2capture
import select
import serial

portx="/dev/ttyUSB0"
bps=9600
timex=None
ser=serial.Serial(portx,bps,timeout=timex)
video = v4l2capture.Video_device("/dev/video0")
video.set_format(1920, 1080, fourcc='MJPG')
video.create_buffers(1)
video.queue_all_buffers()
video.start()
select.select((video,), (), ())


AK = 'NQ4X87cb7E0bbYMcFgjGClur'
SK = 'uGAAkPjcOPRolnlvpZoTjiVWsTusPyOC'
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+AK+'&client_secret='+SK
response = requests.get(host)
access_token = response.json()['access_token']
flag = 0
#cap = cv2.VideoCapture(0)
if response:
    flag = 1


def face_dectect(image64):
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        params = {"image":image64,
                  "image_type":"BASE64",
                  "face_field":"gender,race,age,glasses",
                  "max_face_num":10}
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        return response.json()['result']

def get_image64(*image):
        if image == ():
            image_data = video.read_and_queue()
            frame = cv2.imdecode(numpy.frombuffer(image_data, dtype=numpy.uint8), cv2.IMREAD_COLOR)
        else:
            frame = image[0]
        cv2.imwrite("current_pic.jpg",frame)
        f=open("current_pic.jpg",'rb')
        image = base64.b64encode(f.read())
        image64 = str(image,'utf-8')
        return image64, frame    

def transport_people_facedata(image64, group_id, user_id): # (var, str, str)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
        params = {"image":image64,
                  "image_type":"BASE64",
                  "group_id":group_id,
                  "user_id":user_id,
                  "user_info":"abc",
                  "quality_control":"LOW",
                  "liveness_control":"NORMAL"}

        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        return response.json()['result']    
    
def transport_people_facedata(image64, group_id, user_id): # (var, str, str)
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add"
        params = {"image":image64,
                  "image_type":"BASE64",
                  "group_id":group_id,
                  "user_id":user_id,
                  "user_info":"abc",
                  "quality_control":"LOW",
                  "liveness_control":"NORMAL"}

        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        return response.json()['result']

def plot(frame, left, top, width, height, word, color): #(var, num, top, width, height, str, str)
        cl = (0,255,0)
        if color == 'pink':
            cl = (255,192,203)
        elif color == 'blue':
            cl = (0,0,255)
        elif color == 'brown':
            cl = (165,42,42)
        start_x = numpy.int(left - 0.2*width)
        start_y = numpy.int(top - 0.5*height)
        end_x = numpy.int(left + 1*width)
        end_y = numpy.int(top + 1*height)
        frame = cv2.rectangle(frame,(start_x,start_y),(end_x,end_y), cl,2)
        
        y0, dy = 0, -25

        for i, txt in enumerate(word.split('\n')):
            y = y0+i*dy
            frame = cv2.putText(frame, txt, (start_x,start_y + y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 255, 0), 2, 1)
            
        #frame = cv2.putText(frame,word,(start_x,start_y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2,1) 
                            #图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
        return frame

def M_N(image64,group_id,max_face_num): #(var, str, num)
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/multi-search"
    
    params = {"image": image64,
              "image_type": "BASE64",
              "group_id_list": group_id,
              "max_face_num" : max_face_num,
              "quality_control": "LOW",
              "liveness_control": "NORMAL"}
    
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=params, headers=headers)
    
    return response.json()['result']

def engine(path,group_id):
    time_ = 0
    while(20):
            
            img2,frame2 = get_image64()
            print(str(time_)+'_'+'1')
            try:
                results = M_N(img2,group_id, 10)
                print(str(time_)+'_'+'2'+'successful')
            except:
                print(str(time_)+'_'+'2'+'error')
      
            try:
                result_1 = face_dectect(img2)
                print(str(time_)+'_'+'3'+'successful')
            except:
                print(str(time_)+'_'+'3'+'error')
            x=99
            if results != None:
                for i in range(results['face_num']):
                    if results['face_list'][i]['user_list'] != []:
                        left = results['face_list'][i]['location']['left']
                        top = results['face_list'][i]['location']['top']
                        width = results['face_list'][i]['location']['width']
                        height = results['face_list'][i]['location']['height']

                        word1 = '\n'+'gender:' + result_1['face_list'][i]['gender']['type']
                        word2 = '\n'+'age:' + str(result_1['face_list'][i]['age']-3)
                        word3 = '\n'+'glasses:'+result_1['face_list'][i]['glasses']['type']
                        #word4 = '\n'+'skin:'+result_1['face_list'][i]['race']['type']
                        word4 = '\n' + 'skin:yellow'
                        if word3 == '\nglasses:common':
                            word3 = '\nglasses:Yes'
                        word = 'operator'+ word1 + word2 + word3 + word4
                        color = 'pink'
                        frame2 = plot(frame2, left, top, width, height, word, color)
                        
                        left_eye_x,left_eye_y =  result_1['face_list'][i]['landmark'][0]
                        right_eye_x,right_eye_y = result_1['face_list'][i]['landmark'][1]
                        nose_x,nose_y = result_1['face_list'][i]['landmark'][2]
                        mouse_x,mouse_y = result_1['face_list'][i]['landmark'][3]
                        frame2 = cv2.putText(frame2, 'e', (left_eye_x,left_eye_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'e', (right_eye_x,right_eye_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'n', (nose_x,nose_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'm', (mouse_x,mouse_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        x = i
            if result_1 != None:   
                for i in range(result_1['face_num']):
                    if i != x:
                        left = result_1['face_list'][i]['location']['left']
                        top = result_1['face_list'][i]['location']['top']
                        width = result_1['face_list'][i]['location']['width']
                        height = result_1['face_list'][i]['location']['height']

                        word1 = '\n'+'gender:' + result_1['face_list'][i]['gender']['type']
                        word2 = '\n'+'age:' + str(result_1['face_list'][i]['age']-3)
                        word3 = '\n'+'glasses:'+result_1['face_list'][i]['glasses']['type']
                        #word4 = '\n'+'skin:'+result_1['face_list'][i]['race']['type']
                        word4 = '\n' + 'skin:yellow'
                        if word3 == '\nglasses:common':
                            word3 = '\nglasses:Yes'                        
                        word = 'others'+ word1 + word2 + word3 + word4
                        color = 'pink'
                        frame2 = plot(frame2, left, top, width, height, word, color)
                        
                        left_eye_x,left_eye_y =  result_1['face_list'][i]['landmark'][0]
                        right_eye_x,right_eye_y = result_1['face_list'][i]['landmark'][1]
                        nose_x,nose_y = result_1['face_list'][i]['landmark'][2]
                        mouse_x,mouse_y = result_1['face_list'][i]['landmark'][3]
                        frame2 = cv2.putText(frame2, 'e', (left_eye_x,left_eye_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'e', (right_eye_x,right_eye_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'n', (nose_x,nose_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
                        frame2 = cv2.putText(frame2, 'm', (mouse_x,mouse_y), cv2.FONT_HERSHEY_SIMPLEX,  0.5, (0, 0, 255), 2, 1)
            path_name = path + "/" + str(time_) + '.jpg'
            cv2.imwrite(str(time_)+ '.jpg',frame2)
            print(str(time_)+'_'+'4')
            #cv2.imshow("CSI Camera",frame2)
            time_ = time_ + 1
            print("###################")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
        

    cv2.destroyAllWindows()
    cap.release()
        

def true_engine(path,group_id,user_id):
    #gstreamer_pipeline(flip_method=0)
    print('1')
    time = 0
    #第一步，传输目标人脸信息到库
    while(time < 10):
        print(time)
        img1,frame1 = get_image64()
        try:
            transport_people_facedata(img1, group_id, user_id) # (var, str, str)
        except:
            pass
        time = time + 1
    #sent 'm' to Arduino,now,facedate has transformed completely  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ser.write('m'.encode("gbk"))
    #第二步，获取人群信息并处理,并储存。
    ser.write('g'.encode("gbk"))
    print('start_engine')
    engine(path,group_id)






print("serial info",ser)
print("baudrate:",ser.baudrate)

while(1):
    serial=(ser.read().decode("ascii")) 
    if serial=='1':  # !!!!!!!!!!!!!!!!!!!!!!!!!!   read '1' to start #scan face
       break
true_engine('22','group_competition_12','0')