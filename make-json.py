# coding: utf-8
# from PIL import Image
import os
import sys
import json
import numpy
import cv2
from datetime import datetime
from PIL import Image


def get_rotate_degree(im_obj):
    degree = 0
    if hasattr(im_obj, '_getexif'):
        info = im_obj._getexif()
        ret = dict()
        degree_dict = {1: 0, 3: 180, 6: -90, 8: 90}
        if info:
            orientation = info.get(274, 0)
            degree = degree_dict.get(orientation, 0)
    return degree


def list_img_file(directory):
    """列出目录下所有文件，并筛选出图片文件列表返回"""
    old_list = os.listdir(directory)
    # print old_list
    new_list = []
    tmp_list = set()

    for filename in old_list:
        name, fileformat = filename.split(".")
        if fileformat.lower() == "jpg" or fileformat.lower() == "mp4" or \
           fileformat.lower() == "webm":
            tmp_list.add(name)

    for filename in old_list:
        name, fileformat = filename.split(".")
        if fileformat.lower() == "jpg" or fileformat.lower() == "mp4" or \
           fileformat.lower() == "webm":
            if name in tmp_list:
                tmp_list.remove(name)
                new_list.append(filename)
            else:
                if fileformat.lower() == "mp4" or fileformat.lower() == "webm":
                    new_list.remove(name + '.jpg')
                    new_list.append(filename)
    # print(new_list)
    return new_list


def handle_photo(src_dir, target_file):
    '''根据图片的文件名处理成需要的json格式的数据

    -----------
    最后将data.json文件存到博客的source/photo文件夹下
    '''
    file_list = list_img_file(src_dir)
    file_list.sort(reverse=True)
    list_info = []
    for i in range(len(file_list)):
        filename = file_list[i]
        print(filename.encode("utf-8"))
        date_str, info = filename.split("_")
        info, _type = info.split(".")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        year_month = date_str[0:7]
        if _type == "mp4" or "webm":
            cap = cv2.VideoCapture(src_dir + filename)
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            size = str(width) + "x" + str(height)
        else:
            im = Image.open(src_dir + filename)
            width = im.width
            height = im.height
            if get_rotate_degree(im) == -90:
                size = str(height) + "x" + str(width)
            else:
                size = str(width) + "x" + str(height)
        filename, _ = file_list[i].split(".")
        if i == 0:  # 处理第一个文件
            new_dict = {"date": year_month, "arr": {'year': date.year,
                                                    'month': date.month,
                                                    'link': [filename],
                                                    'text': [info],
                                                    'type': [_type],
                                                    'size': [size]
                                                    }
                        }
            list_info.append(new_dict)
        elif year_month != list_info[-1]['date']:  # 不是同一个月，就新建一个dict
            new_dict = {"date": year_month, "arr": {'year': date.year,
                                                    'month': date.month,
                                                    'link': [filename],
                                                    'text': [info],
                                                    'type': [_type],
                                                    'size': [size]
                                                    }
                        }
            list_info.append(new_dict)
        else:  # 同一个月
            list_info[-1]['arr']['link'].append(filename)
            list_info[-1]['arr']['text'].append(info)
            list_info[-1]['arr']['type'].append(_type)
            list_info[-1]['arr']['size'].append(size)
    
    # list_info = sorted(list_info, key = lambda emp:emp['date'])  # 排序
    final_dict = {"list": list_info}
    with open(target_file, "w") as fp:
        json.dump(final_dict, fp, indent=4, separators=(',', ': '))
    # with open(target_file, "r") as fp:
        # print (json.load(fp)) # appveyor上进行打印会由于utf8发生编码错误

if __name__ == "__main__":
    #handle_photo('photos/', '../themes/next/source/lib/ins/photo.json')
    handle_photo('photos/', 'photo.json')
