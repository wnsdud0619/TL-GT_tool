# -*- coding: utf-8 -*-

"""
Brief  : Traffic light annotation
작성자 : 김준영(21.9.)
수정자 : 박재형(21.9.)
"""
import os
import Tkinter
import numpy as np
import tkFileDialog
from collections import OrderedDict
cls_to_idx = OrderedDict()
cls_to_idx['Green'] = 1
cls_to_idx['Red'] = 2
cls_to_idx['Yellow'] = 3
cls_to_idx['Green_Left'] = 4
cls_to_idx['Red_Left'] = 5
cls_to_idx['Unknown'] = 6

COLORS = [(255, 255, 255), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 255), (0, 0, 0)]


def convert_str_to_index(class_dict):
    index_class = OrderedDict()
    for key, value in class_dict.items():
        index_class[value] = key
    return index_class


def checkResult(_save_dir_path='./result'):
    assert not os.path.exists(_save_dir_path), 'The result folder exists.'


def saveAnnotation(annotations, filename, _save_dir_path='./result'):
    if not os.path.exists(_save_dir_path):
        os.makedirs(_save_dir_path)

    save_file = os.path.join(_save_dir_path, filename)
    np.savetxt(save_file, np.array(annotations), fmt='%s', delimiter=' ')


def loadPath():
    root = Tkinter.Tk()
    root.dir = tkFileDialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
    root.destroy()
    return root.dir


def loadFiles(_base_path, _valid_ext='png'):
    file_list = [loaded_file for loaded_file in os.listdir(_base_path) if loaded_file.endswith('.' + _valid_ext)]
    assert len(file_list) is not 0, 'No Files with \'.$s\' : %s' % (_valid_ext, _base_path)
    file_list.sort()
    print('%d loaded %s in : %s' % (len(file_list), _valid_ext, _base_path))
    return file_list


def check_data_format(name, anno):
    bWrong = len(anno) is not 15
    if bWrong:  # 데이터 개수 체크
        print(name, anno[0], "This result is not correct")

    for idx in range(len(anno)):
        if idx == 0:
            anno[idx] = str(anno[idx])
        elif idx in [2, 4, 5, 6, 7]:
            anno[idx] = int(anno[idx])
        else:
            anno[idx] = float(anno[idx])

    return bWrong, anno


def check_data_type(name, b_box):
    # * 모든 floating point 데이터는 소수점 2째 자리까지만 표현
    # * Ground truth data format은 15자리(score 제외)
    # * Prediction data format은 16자리(score 포함)
    # * DontCare의 경우, 하기 format으로 지정됨
    #       DontCare -1 -1 -10 503.89 169.71 590.61 190.13 -1 -1 -1 -1000 -1000 -1000 -10
    # * 평가 종류별로 희망하지 않은 경우, 하기 format으로 지정 가능
    #   BEV를 희망 - bbox의 y축: -1000
    #   Orientation 희망 x - alpha:-10
    #   3D Object Detection Benchmark 희망x : dimensions : -1 -1 -1 / location : -1000 -1000 -1000

    # 개수 / item  / 예시              / 해당 데이터의 형태(범위)
    # 1 type       / Pedestrian       / str[Car, Van, Truck, Pedestrian, Person_sitting, Cyclist, Tram, Misc, DontCare]
    # 1 truncated  / 0.00             / float[0.0.~1.0] * truncation 비율
    # 1 occluded   / 0                / int[0~3]
    # 1 alpha      / -0.20            / float[-pi~+pi]
    # 4 bbox       / 12.40 43.00 10.73 07.92   / float[px 단위]
    # 3 dimensions / 1.89 0.48 1.20   / float[m 단위]
    # 3 location   / 1.84 1.47 8.41   / float[m 단위]
    # 1 rotation_y / 0.01             / float[-pi~+pi]
    # 1 score      / 0.99             / float[0.0~1.0]

    bWrong = False
    if cls_to_idx.get(b_box[0]) is None:
        print(name, b_box[0], 'class list에 없는 class')
        bWrong = True

    if not 0.0 <= b_box[1] <= 1.0:  # Truncation
        print(name, b_box[0], 'Truncation 범위 밖')
        bWrong = True

    if not 0 <= b_box[2] <= 3:  # Occlusion
        print(name, b_box[0], 'Occlusion 범위 밖')
        bWrong = True

    if not 0 <= abs(b_box[3]) <= 3.14:  # Alpha
        print(name, b_box[0], 'Alpha 범위 밖')
        bWrong = True

    return bWrong


def check_image_boundary(name, img, b_box):
    bWrong = False
    size = img.shape
    if max(b_box[4], b_box[6]) >= size[1]:  # check X
        print(name, b_box[0], 'B.BOX larger than the image was included')
        bWrong = True
    if max(b_box[5], b_box[7]) >= size[0]:  # check Y
        print(name, b_box[0], 'B.BOX larger than the image was included')
        bWrong = True
    if min(b_box[4], b_box[6]) < 0:  # check X
        print(name, b_box[0], 'Negative numbers were included')
        bWrong = True
    if min(b_box[5], b_box[7]) < 0:  # check Y
        print(name, b_box[0], 'Negative numbers were included')
        bWrong = True
    return bWrong


def check_bbox(name, b_box):
    bWrong = False
    if b_box[4] > b_box[6]:
        print(name, '좌우가 바뀐 Bbox')
        bWrong = True
    if b_box[5] > b_box[7]:
        print(name, '상하가 바뀐 Bbox')
        bWrong = True

    return bWrong
