
import torch


def accuracy(inputs, targets, r=0.2):
    batch_size = inputs.shape[0]
    n_stages = inputs.shape[1]
    n_joints = inputs.shape[2]

    inputs = inputs.detach()
    targets = targets.detach()

    if targets.shape[1] != n_stages:
        f_0 = torch.unsqueeze(targets[:, 0, :, :, :], 1)
        targets = torch.cat([f_0, targets], dim=1)

    n_correct = 0
    n_total = batch_size * n_stages * n_joints

    for i in range(batch_size):
        gt = get_preds(targets[i, :, :, :, :])
        preds = get_preds(inputs[i, :, :, :, :])

        w = gt[i, :, 0].max() - gt[i, :, 0].min()
        h = gt[i, :, 1].max() - gt[i, :, 1].min()
        threshold = r * max(w, h)

        scores = torch.norm(preds.sub(gt), dim=2).view(-1)
        n_correct += scores.le(threshold).sum()

    return float(n_correct) / float(n_total)


def coord_accuracy(inputs, gt, r=0.2):
    batch_size = inputs.shape[0]
    n_stages = inputs.shape[1]
    n_joints = inputs.shape[2]

    inputs = inputs.detach()
    gt = gt.detach()

    n_correct = 0
    n_total = batch_size * n_stages * n_joints

    for i in range(batch_size):
        w = gt[i, :, 0].max() - gt[i, :, 0].min()
        h = gt[i, :, 1].max() - gt[i, :, 1].min()
        threshold = r * max(w, h)

        curr_gt = torch.unsqueeze(gt[i], 0).repeat(n_stages, 1, 1)
        scores = torch.norm(inputs[i].sub(curr_gt), dim=2).view(-1)
        n_correct += scores.le(threshold).sum()

    return float(n_correct) / float(n_total)


# Source: https://github.com/bearpaw/pytorch-pose/blob/master/pose/utils/evaluation.py
def get_preds(scores):
    maxval, idx = torch.max(scores.view(scores.size(0), scores.size(1), -1), 2)

    maxval = maxval.view(scores.size(0), scores.size(1), 1)
    idx = idx.view(scores.size(0), scores.size(1), 1) + 1

    preds = idx.repeat(1, 1, 2).float()

    preds[:, :, 0] = (preds[:, :, 0] - 1) % scores.size(3) + 1
    preds[:, :, 1] = torch.floor((preds[:, :, 1] - 1) / scores.size(3)) + 1

    pred_mask = maxval.gt(0).repeat(1, 1, 2).float()
    preds *= pred_mask
    return preds
