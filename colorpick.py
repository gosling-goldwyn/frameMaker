import cv2
import numpy
from numpy import ndarray
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def getMainColor(path:str,width:int,height:int) -> ndarray:
    cv2_img = cv2.imread(path)
    # 行列をBGR→RGBに色変換
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    # 3チャンネルの画像を(縦*横,3)の行列に変換
    cv2_img = cv2_img.reshape((cv2_img.shape[0] * cv2_img.shape[1], 3))

    # KMeansの実行
    cluster = KMeans(n_clusters=5)
    cluster.fit(X=cv2_img)

    # cluster.cluster_centers_にRGBがリストとして格納される

    cluster_centers_arr = cluster.cluster_centers_.astype(int, copy=False)

    allwidth = width * 5

    # ベースレイヤー
    picker = numpy.ones([height, allwidth, 3], dtype="int")*255

    for i, rgb_arr in enumerate(cluster_centers_arr):
        color_img = numpy.ones([height, width, 3], dtype="int")
        for j,rgb in enumerate(rgb_arr):
            color_img[:,:,j] = numpy.ones([height, width], dtype="int") * rgb


        picker[:height,width*i:width*(i+1)] = color_img

    return picker
