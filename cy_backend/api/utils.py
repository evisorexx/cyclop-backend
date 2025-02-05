import requests
import cv2
import numpy as np
import datetime
import os

class_names = ['Ч','ЧК','ЧЖ', 'ЧКЖ']
turpl_class_names = {
     0:'Ч', 1:'ЧК', 2:'ЧЖ', 3:'ЧКЖ'
}

colors = {
     'Ч':(0, 0, 255),
     'ЧК':(0, 255, 255),
     'ЧЖ': (255, 0, 0),
     'ЧКЖ': (0, 255, 0)
}

def sent_to_cv2_server(imencoded):
    file = {'file': ('image.jpg', imencoded.tostring(), 'image/jpeg', {'Expires': '0'})}
    response = requests.post("http://gpu1.bmstu.cy-it.ru:8080/detection", files=file, timeout=5)
    # response = requests.post("http://127.0.0.1:8080/detection", files=file, timeout=5)
    return response


def draw_detections(image, box, label, mask_alpha=0.3):
        mask_img = image.copy()
        det_img = image.copy()

        img_height, img_width = image.shape[:2]
        size = min([img_height, img_width]) * 0.0006
        text_thickness = int(min([img_height, img_width]) * 0.001)

        color = colors[label]
        print(label)
        print(color)

        x1, y1, x2, y2 = map(int, box)

        cv2.rectangle(det_img, (x1, y1), (x2, y2), color, 2)
        cv2.rectangle(mask_img, (x1, y1), (x2, y2), color, -1)

        caption = f'{label}'
        (tw, th), _ = cv2.getTextSize(text=caption, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                    fontScale=size, thickness=text_thickness)
        th = int(th * 1.2)

        cv2.rectangle(det_img, (x1, y1),
                    (x1 + tw, y1 - th), color, -1)
        cv2.rectangle(mask_img, (x1, y1),
                    (x1 + tw, y1 - th), color, -1)
        cv2.putText(det_img, caption, (x1, y1),
                    cv2.FONT_HERSHEY_COMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

        cv2.putText(mask_img, caption, (x1, y1),
                    cv2.FONT_HERSHEY_COMPLEX, size, (255, 255, 255), text_thickness, cv2.LINE_AA)

        return cv2.addWeighted(mask_img, mask_alpha, det_img, 1 - mask_alpha, 0)


def save_media(image, name_of_media):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    path_of_saved_pict = 'media/{}/{}/{}/{}'.format(year, month, day ,name_of_media)
    try:
        os.makedirs('media/{}/{}/{}/'.format(year, month, day))
    except:
        pass
    cv2.imwrite(path_of_saved_pict, image)
    return path_of_saved_pict


def str2list(boxes):
    int_list = [int(num) for num in boxes]
    return int_list


def draw_bbox(frame, bbox, color, thickness=2):
    """
    Рисует ограничивающую рамку на изображении.

    Аргументы:
    - frame: numpy.ndarray, входное изображение
    - bbox: list, список координат ограничивающей рамки в формате [xmin, ymin, xmax, ymax]
    - color: tuple, цвет рамки в формате (R, G, 😎
    - thickness: int, толщина линии рамки (по умолчанию 2)

    Возвращает:
    - None
    """
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]

    # Рисование ограничивающей рамки
    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, thickness)