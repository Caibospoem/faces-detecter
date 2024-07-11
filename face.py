import os
import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
from datetime import datetime
from util import load_config, read_userdata_from_path, custom_round, read_users_from_database
from insert import insert

# 设置设备
device = torch.device("cpu")

# 定义MTCNN进行人脸检测
mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

# 定义Facenet模型
resnet = InceptionResnetV1(pretrained="vggface2").to(device)
resnet.eval()


def upload_users():
    users = []
    config = load_config()
    imgs_dir = config["imgs_dir"]
    imgs = os.listdir(imgs_dir)
    img_paths = [imgs_dir + img for img in imgs]
    for img_path in img_paths:
        img = Image.open(img_path)
        img = mtcnn(img)
        img = img.unsqueeze(0).to(device)
        feature = resnet(img)
        feature = feature.detach().numpy()
        feature = [custom_round(float(f)) for f in feature[0]]
        user_data = read_userdata_from_path(img_path)
        user_data.append(feature)
        user_data = tuple(user_data)
        users.append(user_data)

    insert(users)
    return tuple(user_data)


def detect_user():
    users = read_users_from_database()
    data_features = [torch.tensor(users[i]["features"]) for i in range(len(users))]
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        imgs = mtcnn(pil_img)
        landmarks, _, _ = mtcnn.detect(pil_img, landmarks=True)
        box = 0
        flag = 0

        if imgs is not None:
            imgs = imgs.unsqueeze(0).to(device)
            features = [resnet(face.unsqueeze(0)) for face in imgs]

            for i, feature in enumerate(features):
                for index, data_feature in enumerate(data_features):
                    similarity = torch.dist(feature, data_feature, p=2)
                    print(similarity)
                    if similarity < 0.78:
                        print("发现匹配人员:", users[index]["name"], similarity)
                        current_time = datetime.now()
                        print("发现时间:", current_time.strftime("%Y-%m-%d %H:%M:%S"))
                        frame_box = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                        landmark = landmarks[i]
                        x1, y1, x2, y2 = landmark[:4].astype(int)
                        cv2.rectangle(frame_box, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        box = frame_box
                        flag = 1

        if flag == 0:
            yield frame
        else:
            yield box

    cap.release()
    cv2.destroyAllWindows()
