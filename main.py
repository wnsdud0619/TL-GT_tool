# -*- coding: utf-8 -*-

"""
Brief  : Traffic light annotation
작성자 : 김준영(21.9.)
수정자 : 박재형(21.9.)
"""

import util
import cv2
import cvui
import os
import numpy as np
idx_to_cls = util.convert_str_to_index(util.cls_to_idx)


def drawButton(img, idx):
    width_step = 652
    for index, (key, elem) in enumerate(idx_to_cls.items()):
        if cvui.button(img, width_step, 40 + idx * 200, 70, 30, elem):
            return key
        width_step += 80


def main():
    util.checkResult()
    cvui.init('Annotation')
    png_load_button = False
    txt_load_button = False
    changed_TL_type = [None, None, None]
    cnt = 0

    while True:
        ui_img = np.zeros((700, 1150, 3), np.uint8)
        if cvui.button(ui_img, 20, 20, 100, 30, 'load png'):
            img_folder_path = util.loadPath()
            #img_folder_path = 'C:/Users/stillrunning/Desktop/TL_annotation/png'
            img_file_list = util.loadFiles(img_folder_path)
            png_load_button = True

        if cvui.button(ui_img, 150, 20, 100, 30, 'load txt'):
            txt_folder_path = util.loadPath()
            #txt_folder_path = 'C:/Users/stillrunning/Desktop/TL_annotation/txt'
            txt_file_list = util.loadFiles(txt_folder_path, 'txt')
            txt_load_button = True

        if png_load_button & txt_load_button:
            assert len(img_file_list) == len(txt_file_list), 'The file pairs do not match(Image : %d, Annotation : %d)' % (len(img_file_list), len(txt_file_list))
            img_file = os.path.join(img_folder_path, img_file_list[cnt])
            label_file = os.path.join(txt_folder_path, os.path.basename(img_file).replace("png", "txt"))
            assert os.path.isfile(label_file), 'No annotation file(%s)' % label_file
            cvui.printf(ui_img, 270, 25, 0.6, 0xffffff, "File name : %s" % os.path.basename(img_file))

            input_img = cv2.imread(img_file)
            display_img = input_img.copy()
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

                    cv2.rectangle(display_img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 3)
                    crop_img = input_img[ymin:ymax, xmin:xmax]
                    resize_roi_crop = cv2.resize(crop_img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                    ui_img[100 + idx * 200:100 + idx * 200 + resize_roi_crop.shape[0], 652:652 + resize_roi_crop.shape[1]] = resize_roi_crop

                    if drawButton(ui_img, idx):
                        flag = drawButton(ui_img, idx)
                        for i in range(idx, len(changed_TL_type)):
                            changed_TL_type[i] = flag

            for idx in range(len(annotations)):
                if changed_TL_type[idx]:
                    annotations[idx][0] = idx_to_cls[changed_TL_type[idx]]
                cvui.rect(ui_img, 652 + (80 * (util.cls_to_idx[annotations[idx][0]]-1)), 40 + idx * 200, 70, 30, 0xff0000)

            display_img = cv2.resize(display_img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
            ui_img[60:60 + display_img.shape[0], 20:20 + display_img.shape[1]] = display_img

        cvui.update()
        cvui.imshow('Annotation', ui_img)

        key = cv2.waitKey(1)
        if key == 27:  # esc key
            break
        elif key == ord('a'):
            util.saveAnnotation(annotations, txt_file_list[cnt])
            cnt = cnt - 1
            if cnt <= 0:
                cnt = 0
            else:
                changed_TL_type = [None, None, None]
        elif key == ord('d'):
            util.saveAnnotation(annotations, txt_file_list[cnt])
            cnt = cnt + 1
            if cnt >= len(img_file_list):
                cnt = len(img_file_list) - 1
            else:
                changed_TL_type = [None, None, None]


if __name__ == '__main__':
    main()
