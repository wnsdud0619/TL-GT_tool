# -*- coding: utf-8 -*-

"""
Brief  : Traffic light annotation
작성자 : 김준영(21.9.)
"""
import multiprocessing
import threading
import util
import cv2
import os
idx_to_cls = util.convert_str_to_index(util.cls_to_idx)


def draw_image(pair_list, result_path):
    for pair in pair_list:
        img_file = pair[0]
        label_file = pair[1]
        img = cv2.imread(img_file)
        with open(label_file, 'r') as anno_file:
            # type truncated occluded alpha left top right bottom height width length x y z rotation_y score
            annotations = [line.strip().split(' ') for line in anno_file.readlines()]
            if not annotations:
                return

            for idx in range(len(annotations)):
                anno = annotations[idx]
                result_cout, anno = util.check_data_format(label_file, anno)
                result_bbox = util.check_bbox(label_file, anno)  # bbox check
                result_bound = util.check_image_boundary(label_file, img, anno)  # boundary check
                result_type = util.check_data_type(label_file, anno)  # data type check
                if result_bbox or result_bound or result_type or result_cout:
                    return

                xmin = anno[4]
                ymin = anno[5]
                xmax = anno[6]
                ymax = anno[7]

                cv2.putText(img, anno[13], (2448/2, 2048/2), cv2.FONT_HERSHEY_SIMPLEX, 1, util.COLORS[util.cls_to_idx[anno[13]]], 2)
                cv2.putText(img, anno[0], (xmin-5, ymin-5), cv2.FONT_HERSHEY_SIMPLEX, 1, util.COLORS[util.cls_to_idx[anno[0]]], 2)
                cv2.rectangle(img, (xmin, ymin), (xmax, ymax), util.COLORS[util.cls_to_idx[anno[0]]], 3)

        save_file = os.path.join(result_path, os.path.basename(img_file))
        cv2.imwrite(save_file, img)
        print('%s is done' % save_file)


def main():
    root_path = '/home/stillrunning/code/TL_annotation'
    img_folder_path = os.path.join(root_path, 'png')
    txt_folder_path = os.path.join(root_path, 'result')
    result_path = './display'
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    image_list = util.loadFiles(img_folder_path)

    paired_img_list = []
    paired_label_list = []
    for img_name in image_list:
        img_file = os.path.join(img_folder_path, img_name)
        label_file = os.path.join(txt_folder_path, os.path.basename(img_file).replace("png", "txt"))
        assert os.path.isfile(label_file), 'No annotation file(%s)' % label_file
        paired_img_list.append(img_file)
        paired_label_list.append(label_file)

    pairs = zip(paired_img_list, paired_label_list)

    thread_count = multiprocessing.cpu_count()
    sliced_num = len(pairs) / thread_count

    threads = []
    for idx in range(thread_count):
        start = idx * sliced_num
        end = (idx + 1) * sliced_num if idx < range(thread_count)[-1] else len(pairs)
        thread = threading.Thread(target=draw_image, args=(pairs[start:end], result_path, ),)
        thread.start()
        threads.append(thread)

    # 메인 스레드는 각 스레드의 작업이 모두 끝날 때까지 대기
    for thread in threads:
        thread.join()

    print('Done')


if __name__ == '__main__':
    main()
