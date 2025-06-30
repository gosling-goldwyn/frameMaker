import cv2
import numpy as np
from sklearn.cluster import KMeans

from src.constants import KMEANS_CLUSTERS, SATURATION_THRESHOLD, BRIGHTNESS_THRESHOLD

def _get_filtered_pixels(img: np.ndarray) -> np.ndarray:
    """
    画像から彩度と明度に基づいてフィルタリングされたピクセルを取得します。

    Args:
        img (np.ndarray): 処理する画像データ (NumPy 配列)。

    Returns:
        np.ndarray: フィルタリングされたピクセルデータ。
    """
    cv2_img = img.reshape((img.shape[0] * img.shape[1], 3))

    img_8bit = (img * 255).astype(np.uint8)
    hsv_image = cv2.cvtColor(img_8bit, cv2.COLOR_BGR2HSV).reshape(
        (img.shape[0] * img.shape[1], 3)
    )
    hsv_image = hsv_image / 255
    saturation_pixel = hsv_image[:, 1] / hsv_image[:, 1].max()
    brightness_pixel = hsv_image[:, 2] / hsv_image[:, 2].max()

    saturation_mask = saturation_pixel > SATURATION_THRESHOLD
    brightness_mask = brightness_pixel > BRIGHTNESS_THRESHOLD
    filtered_pixels = cv2_img[saturation_mask & brightness_mask]
    return filtered_pixels


def getMainColorKmeans(img: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    画像から主要な色を抽出し、それらを表すカラーバー画像を生成します。
    KMeans クラスタリングを使用して色を特定します。

    Args:
        img (np.ndarray): 処理する画像データ (NumPy 配列)。
        width (int): 生成するカラーバーの各色の幅。
        height (int): 生成するカラーバーの高さ。

    Returns:
        np.ndarray: 主要な色を表すカラーバー画像データ (NumPy 配列)。
    """
    filtered_pixels = _get_filtered_pixels(img)

    cluster = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=0, n_init=10)
    cluster.fit(filtered_pixels)

    cluster_centers_arr = cluster.cluster_centers_ * 255
    cluster_centers_arr = cluster_centers_arr.astype("int")

    hsv_centers = cv2.cvtColor(np.uint8([cluster_centers_arr]), cv2.COLOR_RGB2HSV)[0]

    sorted_indices = np.argsort(hsv_centers[:, 0])
    cluster_centers_arr = cluster_centers_arr[sorted_indices]

    allwidth = width * KMEANS_CLUSTERS

    picker = np.ones([height, allwidth, 3], dtype="int") * 255

    for i, rgb_arr in enumerate(cluster_centers_arr):
        color_img = np.ones([height, width, 3], dtype="int")
        for j, rgb in enumerate(rgb_arr):
            color_img[:, :, j] = np.ones([height, width], dtype="int") * rgb

        picker[:height, width * i : width * (i + 1)] = color_img

    return picker


def getMainColorRGBValue(img: np.ndarray) -> list[str]:
    """
    画像から主要な色の RGB 値をリストとして取得します。
    KMeans クラスタリングを使用して色を特定します。

    Args:
        img (np.ndarray): 処理する画像データ (NumPy 配列)。

    Returns:
        list[str]: 主要な色の RGB 値のリスト (例: ["RRGGBB", ...])。
    """
    filtered_pixels = _get_filtered_pixels(img)

    cluster = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=0, n_init=10)
    cluster.fit(filtered_pixels)

    cluster_centers_arr = cluster.cluster_centers_ * 255
    cluster_centers_arr = cluster_centers_arr.astype("int")

    return [f"{e[0]:02x}{e[1]:02x}{e[2]:02x}" for e in cluster_centers_arr.tolist()]
