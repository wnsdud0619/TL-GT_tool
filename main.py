# -*- coding: utf-8 -*-

"""
Brief  : Traffic light annotation
작성자 : 김준영(21.9.)
수정자 : 박재형(21.9.)
수정자 : 김준영(22.6.)
"""

import util
import cv2
import cvui
import os
import os.path
import numpy as np
idx_to_cls = util.convert_str_to_index(util.cls_to_idx)
save_dir_path = './result'

# 개별 신호등 annotation btn
def drawBtn4EachTL(img, idx):
    width_step = 652
    for index, (key, elem) in enumerate(idx_to_cls.items()):
        if cvui.button(img, width_step, 240 + idx * 200, 70, 30, elem):
            return key
        width_step += 80

# 대표 신호등 annotation btn
def drawBtn4RepresentativeTL(img):
    width_step = 652
    for index, (key, elem) in enumerate(idx_to_cls.items()):
        if cvui.button(img, width_step, 40, 70, 30, elem):
            return key
        width_step += 80


def main():
    util.checkResult(save_dir_path)
    cvui.init('Annotation')
    png_load_button = False
    txt_load_button = False
    changed_TL_type = [None, None, None]  # 개별 신호등에 대한 타입변화
    changed_Represent_TL_type = None  # 대표 신호등에 대한 타입변화
    cnt = 0

    while True:
        ui_img = np.zeros((800, 1150, 3), np.uint8)
        if cvui.button(ui_img, 20, 20, 100, 30, 'load png'):
            #img_folder_path = util.loadPath()
            img_folder_path = '/media/dgist/Samsung_T5/220620/211103_TL_KIAPI/png'
            img_file_list = util.loadFiles(img_folder_path)
            png_load_button = True

        if cvui.button(ui_img, 150, 20, 100, 30, 'load txt'):
            #txt_folder_path = util.loadPath()
            txt_folder_path = '/home/dgist/Downloads/3_작업 완료_label만 업로드/211103_TL_KIAPI/label'
            txt_file_list = util.loadFiles(txt_folder_path, 'txt')
            txt_load_button = True

        if png_load_button & txt_load_button:
            assert len(img_file_list) == len(txt_file_list), 'The file pairs do not match(Image : %d, Annotation : %d)' % (len(img_file_list), len(txt_file_list))
            img_file = os.path.join(img_folder_path, img_file_list[cnt])
            label_file = os.path.join(txt_folder_path, os.path.basename(img_file).replace("png", "txt"))
            
            # result label file이 존재하면 해당 파일로 정보 load
            result_label_file = os.path.join(save_dir_path, os.path.basename(img_file).replace("png", "txt"))
            if os.path.isfile(result_label_file):
                label_file = result_label_file

            assert os.path.isfile(label_file), 'No annotation file(%s)' % label_file
            cvui.printf(ui_img, 270, 25, 0.6, 0xffffff, "File name : %s" % os.path.basename(img_file))
            input_img = cv2.imread(img_file)
            display_img = input_img.copy()

            bbox_y = 0
            with open(label_file, 'r') as anno_file:
                # type truncated occluded alpha left top right bottom height width length x y z rotation_y score
                annotations = [line.strip().split(' ') for line in anno_file.readlines()]
                if not annotations:
                    break

                for idx in range(len(annotations)):
                    anno = annotations[idx]
                    result_cout, anno = util.check_data_format(label_file, anno)
                    result_bbox = util.check_bbox(label_file, anno)  # bbox check
                    result_bound = util.check_image_boundary(label_file, input_img, anno)  # boundary check
                    result_type = util.check_data_type(label_file, anno)  # data type check
                    if result_bbox or result_bound or result_type or result_cout:
                        break

                    xmin = anno[4]
                    ymin = anno[5]
                    xmax = anno[6]
                    ymax = anno[7]
                    bbox_y = ymin

                    cv2.rectangle(display_img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 3)
                    crop_img = input_img[ymin:ymax, xmin:xmax]
                    resize_roi_crop = cv2.resize(crop_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                    ui_img[280 + idx * 200:280 + idx * 200 + resize_roi_crop.shape[0], 652:652 + resize_roi_crop.shape[1]] = resize_roi_crop

                    if drawBtn4EachTL(ui_img, idx):
                        flag = drawBtn4EachTL(ui_img, idx)
                        for i in range(idx, len(changed_TL_type)):
                            changed_TL_type[i] = flag

                    if drawBtn4RepresentativeTL(ui_img):
                        flag = drawBtn4RepresentativeTL(ui_img)
                        changed_Represent_TL_type = flag

            for idx in range(len(annotations)):
                if changed_TL_type[idx]:
                    annotations[idx][0] = idx_to_cls[changed_TL_type[idx]]
                cvui.rect(ui_img, 652 + (80 * (util.cls_to_idx[annotations[idx][0]]-1)), 240 + idx * 200, 70, 30, 0xff0000)

            for idx in range(len(annotations)):
                if changed_Represent_TL_type:
                    annotations[idx][13] = idx_to_cls[changed_Represent_TL_type]
                cvui.rect(ui_img, 652 + (80 * (util.cls_to_idx[annotations[idx][13]]-1)), 40, 70, 30, 0xff0000)

            bbox_y = 0 if (bbox_y - 250) < 0 else (bbox_y - 250)
            crop_img = input_img[bbox_y:bbox_y+500, 0:input_img.shape[1]]
            ratio = 150.0/crop_img.shape[0] if 470.0/crop_img.shape[1] > 150.0/crop_img.shape[0] else 470.0/crop_img.shape[1]
            resize_roi_crop = cv2.resize(crop_img, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)
            ui_img[80:80+resize_roi_crop.shape[0], 652:652+resize_roi_crop.shape[1]] = resize_roi_crop

            display_img = cv2.resize(display_img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
            ui_img[60:60 + display_img.shape[0], 20:20 + display_img.shape[1]] = display_img

        cvui.update()
        cvui.imshow('Annotation', ui_img)

        key = cv2.waitKey(1)
        if key == 27:  # esc key
            break
        elif key == ord('a'):
            util.saveAnnotation(annotations, txt_file_list[cnt], save_dir_path)
            cnt = cnt - 1
            if cnt <= 0:
                cnt = 0
            else:
                changed_TL_type = [None, None, None]
                changed_Represent_TL_type = None
        elif key == ord('d'):
            util.saveAnnotation(annotations, txt_file_list[cnt], save_dir_path)
            cnt = cnt + 1
            if cnt >= len(img_file_list):
                cnt = len(img_file_list) - 1
            else:
                changed_TL_type = [None, None, None]
                changed_Represent_TL_type = None


if __name__ == '__main__':
    main()
