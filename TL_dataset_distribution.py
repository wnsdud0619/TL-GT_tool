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

CLASSES = ['Green', 'Red', 'Yellow', 'Green_Left', 'Red_Left', 'Unknown']

anno_path = sys.argv[1] if len(sys.argv) > 1 else "./result"

label_list = glob.glob(anno_path + '/*.txt')

num_object = []
for label in label_list:
    with open(label) as label_file:
        while True:
            anno = label_file.readline().split()
            if not anno:
                break

            if not anno[0] in CLASSES:
                print(label, '[%s] isn\'t at list' % anno[0])
                raw_input('잘못된 Annotation 존재(계속하려면 아무키 입력) : %s' % label)

            num_object.append(anno[0])
print('"%s" is Loaded' % anno_path)
print('Image : %d' % len(label_list))

count = Counter(num_object)
className = []
classCount = []

for key in CLASSES:
    className.append(key)
    classCount.append(count[key])

print('\t'.join(str(x) for x in className))
print('\t'.join(str(x) for x in classCount))

