import cv2
import numpy as np
from sklearn.cluster import KMeans


def getMainColorKmeans(img: np.ndarray, width: int, height: int) -> np.ndarray:
    # 3チャンネルの画像を(縦*横,3)の行列に変換
    cv2_img = img.reshape((img.shape[0] * img.shape[1], 3))

    # 彩度を計算
    img_8bit = (img * 255).astype(np.uint8)
    hsv_image = cv2.cvtColor(img_8bit, cv2.COLOR_BGR2HSV).reshape(
        (img.shape[0] * img.shape[1], 3)
    )
    hsv_image = hsv_image / 255
    saturation_pixel = hsv_image[:, 1] / hsv_image[:, 1].max()  # 彩度
    brightness_pixel = hsv_image[:, 2] / hsv_image[:, 2].max()  # 明度
    saturation_threshold = 0.5
    brightness_threshold = 0.5
    saturation_mask = saturation_pixel > saturation_threshold
    brightness_mask = brightness_pixel > brightness_threshold
    filtered_pixels = cv2_img[saturation_mask & brightness_mask]

    # KMeansの実行
    cluster = KMeans(n_clusters=5)
    cluster.fit(filtered_pixels)

    # cluster.cluster_centers_にRGBがリストとして格納される

    cluster_centers_arr = cluster.cluster_centers_ * 255
    cluster_centers_arr = cluster_centers_arr.astype("int")

    # RGBをHSVに変換
    hsv_centers = cv2.cvtColor(np.uint8([cluster_centers_arr]), cv2.COLOR_RGB2HSV)[0]

    # 彩度でソート
    sorted_indices = np.argsort(hsv_centers[:, 0])
    cluster_centers_arr = cluster_centers_arr[sorted_indices]

    allwidth = width * 5

    # ベースレイヤー
    picker = np.ones([height, allwidth, 3], dtype="int") * 255

    for i, rgb_arr in enumerate(cluster_centers_arr):
        color_img = np.ones([height, width, 3], dtype="int")
        for j, rgb in enumerate(rgb_arr):
            color_img[:, :, j] = np.ones([height, width], dtype="int") * rgb

        picker[:height, width * i : width * (i + 1)] = color_img

    return picker
