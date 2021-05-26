from datetime import datetime

import cv2
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def generate_random_square():
    color = (1, 1, 1)
    img = np.zeros((128, 128, 1), np.uint8)
    square_size = 10 + np.random.randint(int(128 / 8))
    square_location = (
        np.random.randint(128 - square_size),
        np.random.randint(128 - square_size),
    )
    cv2.rectangle(
        img,
        square_location,
        (square_location[0] + square_size, square_location[1] + square_size),
        color,
        -1,
    )
    return img


def normalize(d: np.ndarray):
    d_min = np.amin(d)
    d_max = np.amax(d)
    return (d - d_min) / (d_max)


def load_img(img_path: str, size: tuple = (128, 128, 3)) -> np.ndarray:
    data = Image.open(img_path, mode="r")
    data = cv2.resize(
        np.asarray(data), dsize=(size[0], size[1]), interpolation=cv2.INTER_LANCZOS4
    )
    if size[-1] == 1:
        data = data.mean(axis=-1, keepdims=True)
    data = np.array(data).astype(np.float32) / 255.0  # uint8 -> float32
    return data


def combine(
    mask: np.ndarray, foreground: np.ndarray, background: np.ndarray, blur: bool = False
) -> np.ndarray:
    if blur:
        # select random odd kernel size
        kernel_size = int(np.random.choice([1, 3, 5, 7, 9]))
        sigma = np.random.uniform(0.1, 3)  # select deviation
        mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), sigma)
    mask = np.stack([mask] * foreground.shape[2], axis=-1)
    combination = mask * foreground + (1 - mask) * background
    return combination


def plot(img):
    plt.imshow(img)
    plt.axis("off")
    plt.show()


def plot_data_item(data_item):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(data_item["reference"].permute(1, 2, 0))
    axes[0].set_title("reference")
    axes[0].axis("off")
    axes[1].imshow(data_item["positive"].permute(1, 2, 0))
    axes[1].set_title("positive")
    axes[1].axis("off")
    axes[2].imshow(data_item["negative"].permute(1, 2, 0))
    axes[2].set_title("negative")
    axes[2].axis("off")
    plt.show()


def get_binary_mask(image: np.ndarray, gaussian_blur: bool = False) -> np.ndarray:
    mask = cv2.threshold(image.mean(axis=-1), 0.5, 1, cv2.THRESH_BINARY_INV)[1]
    if gaussian_blur:
        # select random odd kernel size
        kernel_size = int(np.random.choice([1, 3, 5, 7, 9]))
        sigma = np.random.uniform(0.1, 3)  # select deviation
        mask = cv2.GaussianBlur(mask, (kernel_size, kernel_size), sigma)
    return np.expand_dims(mask, axis=-1)


def create_random_gradient_image(
    size: tuple, low: float = 0.0, high: float = 1.0
) -> np.ndarray:
    color_a = np.random.uniform(low, high)
    color_b = np.random.uniform(low, high)
    locations = (np.random.randint(size[0]), np.random.randint(size[0]))
    while locations[0] == locations[1]:
        locations = (np.random.randint(size[0]), np.random.randint(size[0]))
    x1, x2 = min(locations), max(locations)
    gradient = np.arange(color_a, color_b, ((color_b - color_a) / (x2 - x1)))
    gradient = gradient[: x2 - x1]
    assert len(gradient) == x2 - x1, f"failed: {len(gradient)} vs {x2 - x1}"
    vertical_gradient = np.concatenate(
        [np.ones(x1) * color_a, gradient, np.ones(size[0] - x2) * color_b]
    )
    image = np.stack([vertical_gradient] * size[1], axis=1).reshape(size)
    return image


def get_date_time_tag() -> str:
    return str(datetime.strftime(datetime.now(), format="%y-%m-%d_%H-%M-%S"))
