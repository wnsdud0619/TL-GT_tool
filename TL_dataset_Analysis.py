# -*- coding: utf-8 -*-

"""
Brief  : Traffic Light Annotation Distribution Check
작성자 : 김동욱(21.09.)
수정자 :
"""
import os
import sys
import glob
from collections import Counter

anno_path = sys.argv[1] if len(sys.argv) > 1 else "./all_data"
label_list = glob.glob(anno_path + '/*.txt')

width = []
height = []
ratio = []

data = open('result.txt', 'w')

for label in label_list:
    with open(label) as label_file:
        while True:
            anno = label_file.readline().split()
            if not anno:
                break
            width.append(float(anno[6]) - float(anno[4]))
            height.append(float(anno[7]) - float(anno[5]))
            ratio.append((float(anno[6]) - float(anno[4]))/(float(anno[7]) - float(anno[5])))
            data.write("%d, %d\n" % (float(anno[6]) - float(anno[4]), float(anno[7]) - float(anno[5])))

data.close()

print('"%s" is Loaded' % anno_path)
print('Image : %d' % len(label_list))
print('width min : %f / width max : %f' %(min(width), max(width)))
print('height min : %f / height max : %f' %(min(height), max(height)))
print('ratio min : %f / ratio max : %f' %(min(ratio), max(ratio)))

