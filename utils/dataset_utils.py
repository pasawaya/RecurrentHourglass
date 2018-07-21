
import numpy as np
from skimage.draw import circle, line
from skimage.io import imshow
from matplotlib import pyplot as plt
import torch


def to_numpy(data):
    n = len(data)
    x, y, vis = np.zeros(n), np.zeros(n), np.zeros(n)
    for p in range(n):
        x[p] = data[str(p)][0]
        y[p] = data[str(p)][1]
        vis[p] = data[str(p)][2]
    return x, y, vis


def visualize_input(image, x, y, vis):
    limbs = [(0, 1), (1, 2), (2, 3), (2, 8), (3, 8), (3, 4), (4, 5), (8, 9), (8, 12),
             (8, 13), (10, 11), (11, 12), (12, 13), (6, 7), (6, 13)]

    image = image.astype(np.uint8)

    for p_x, p_y, p_vis in zip(x, y, vis):
        if p_vis:
            rr, cc = circle(p_y, p_x, 4)
            image[rr, cc] = (255, 255, 255)

    for i, j in limbs:
        if vis[i] and vis[j]:
            rr, cc = line(y[i], x[i], y[j], x[j])
            image[rr, cc] = (0, 255, 0)

    imshow(image)
    plt.show()


def compute_label_map(x, y, visibility, size, sigma, stride):
    if len(x.shape) < 2:
        x = np.expand_dims(x, 0)
        y = np.expand_dims(y, 0)
        visibility = np.expand_dims(visibility, 0)

    t = x.shape[0]
    n_joints = x.shape[1]
    label_size = np.floor((size - 0.5) / stride).astype(int)
    label_map = np.zeros((t, n_joints + 1, label_size, label_size))
    start = (stride / 2.) - 0.5
    for t in range(t):
        for p in range(n_joints):
            if visibility[t, p] > 0:
                center_x, center_y = x[t, p], y[t, p]
                X, Y = np.meshgrid(np.linspace(0, label_size, label_size), np.linspace(0, label_size, label_size))
                X = (X - 1) * stride + start - center_x
                Y = (Y - 1) * stride + start - center_y
                d2 = X * X + Y * Y
                exp = d2 * 0.5 / sigma / sigma
                label = np.exp(-exp)
                label[label < 0.01] = 0
                label[label > 1] = 1
            else:
                label = np.zeros((label_size, label_size))
            label_map[t, p, :, :] = label
    return torch.from_numpy(label_map).float()