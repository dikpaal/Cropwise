# -*- coding: utf-8 -*-
"""Leaf_Recognition.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AP1sU3yh85_iT37Yp3LbOD3jNRBJKnfc
"""

from google.colab import drive
drive.mount('/content/drive')



import os
import cv2
import numpy as np
import pandas as pd
import matplotlib as plt

csv_file = '/content/drive/My Drive/train.csv'
output_dir = '/content/drive/My Drive/masks'

# Read the CSV file into a Pandas DataFrame
data = pd.read_csv(csv_file)

from torch.utils.data import Dataset as BaseDataset

import os
import cv2
import numpy as np
from torch.utils.data import Dataset as BaseDataset

class Dataset(BaseDataset):
    def __init__(self, data, images_dir, augmentation=None, preprocessing=None):
        self.data = data
        self.images_dir = images_dir
        self.augmentation = augmentation
        self.preprocessing = preprocessing

    def __getitem__(self, i):
        image_id = self.data.loc[i, "image_id"]

        print(f"Image ID: {image_id}")

        image_path = os.path.join(self.images_dir, image_id)

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")

        # Create a blank mask and extract bounding box info
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)

        # Print a message just before entering the loop

        # Iterate through rows to create masks based on bounding boxes
        for _, row in self.data[self.data["image_id"] == image_id].iterrows():
            bbox = eval(row['bbox'])
            x, y, w, h = bbox

            # Ensure bounding box coordinates are within image dimensions
            x, y, w, h = max(0, x), max(0, y), min(w, width - x), min(h, height - y)

            mask[y:y+h, x:x+w] = 1

        # Print a message after the loop

        if self.augmentation:
            sample = self.augmentation(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        if self.preprocessing:
            sample = self.preprocessing(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        return image, mask

    def __len__(self):
        return len(self.data)







import matplotlib.pyplot as plt

def visualize(image, mask, label = None, truth = None, augment = False):
  if truth is None:
    plt.figure(figsize = (14, 20))
    plt.subplot(1,2,1)
    plt.imshow(image)
    if augment == False:
      plt.title(f"{'Original Image'}")
    else :
      plt.title(f"{'augmented image'}")
    plt.subplot(1,2,2)
    plt.imshow(mask)
    if label is not None:
      plt.title(f"{label.capitalize()}")

import pandas as pd
from sklearn.model_selection import train_test_split

# Assuming you load the data from a CSV file
data_file = '/content/drive/My Drive//train.csv'
images_dir = '/content/drive/My Drive/trainn'
all_data = pd.read_csv(data_file)
print(all_data)

# Split into train_data and remaining_data
train_data, remaining_data = train_test_split(all_data, test_size=0.3, random_state=42)

# Further split remaining_data into validation_data and test_data
validation_data, test_data = train_test_split(remaining_data, test_size=0.5, random_state=42)

# Assuming CLASSES is defined somewhere in your code


# Assuming the Dataset class is defined and imported correctly
train_dataset = Dataset(train_data, images_dir)
test_dataset = Dataset(test_data, images_dir)
validation_dataset = Dataset(validation_data, images_dir)

# Visualize samples from each dataset

try:
  for i in range(len(train_dataset)):
    if i in train_dataset.data.index:
      image, mask = train_dataset[i]
      visualize(image=image, mask=mask.squeeze())  # Assuming visualize expects channels last
    else:
      print("")
except Exception as e:
    print(f"Other error: {type(e).__name__} - {e}")
finally:
  plt.close()

import albumentations as albu
def get_training_augmentation():
    train_transform = [
        albu.Resize(256, 416, p=1),
        albu.HorizontalFlip(p=0.5),
        albu.OneOf([
            albu.RandomBrightnessContrast(brightness_limit=0.4, contrast_limit=0.4, p=1),
            albu.CLAHE(p=1),
            albu.HueSaturationValue(p=1)
        ], p=0.9),
        albu.GaussNoise(p=0.2),
    ]
    return albu.Compose(train_transform)

def get_validation_augmentation():
    """Add paddings to make image shape divisible by 32"""
    test_transform = [
        albu.PadIfNeeded(256, 416)
    ]
    return albu.Compose(test_transform)

def to_tensor(x, **kwargs):
    if len(x.shape) == 3:
        # If the input has three dimensions, transpose the axes
        return x.transpose(2, 0, 1).astype('float32')
    elif len(x.shape) == 2:
        # If the input has two dimensions, add a channel dimension
        return np.expand_dims(x, axis=0).astype('float32')
    else:
        raise ValueError(f"Unsupported input shape: {x.shape}")

def get_preprocessing(preprocessing_fn):
  _transform = [
      albu.Lambda(image = preprocessing_fn),
      albu.Lambda(image = to_tensor, mask = to_tensor),
  ]
  return albu.Compose(_transform)

import numpy as np
import matplotlib.pyplot as plt  # Importing matplotlib.pyplot

def visualizeData(**images):
    """PLot images in one row."""
    n = len(images)
    plt.figure(figsize=(16, 5))
    for i, (name, image) in enumerate(images.items()):
        plt.subplot(1, n, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.title(' '.join(name.split('_')).title())
        plt.imshow(image)
    plt.show()

from torch.utils.data import DataLoader, ConcatDataset

augmented_dataset = Dataset(
    train_data,
    images_dir,
    augmentation = get_training_augmentation(),
)
combined_train_dataset = ConcatDataset([train_data, augmented_dataset])

for i in range(0):
    image, mask = augmented_dataset[4]
    visualizationDatea(image=image, mask=mask)



import re
import torch.nn as nn


class BaseObject(nn.Module):
    def __init__(self, name=None):
        super().__init__()
        self._name = name

    @property
    def __name__(self):
        if self._name is None:
            name = self.__class__.__name__
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        else:
            return self._name


class Metric(BaseObject):
    pass


class Loss(BaseObject):
    def __add__(self, other):
        if isinstance(other, Loss):
            return SumOfLosses(self, other)
        else:
            raise ValueError("Loss should be inherited from `Loss` class")

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, value):
        if isinstance(value, (int, float)):
            return MultipliedLoss(self, value)
        else:
            raise ValueError("Loss should be inherited from `BaseLoss` class")

    def __rmul__(self, other):
        return self.__mul__(other)


class SumOfLosses(Loss):
    def __init__(self, l1, l2):
        name = "{} + {}".format(l1.__name__, l2.__name__)
        super().__init__(name=name)
        self.l1 = l1
        self.l2 = l2

    def __call__(self, *inputs):
        return self.l1.forward(*inputs) + self.l2.forward(*inputs)


class MultipliedLoss(Loss):
    def __init__(self, loss, multiplier):

        # resolve name
        if len(loss.__name__.split("+")) > 1:
            name = "{} * ({})".format(multiplier, loss.__name__)
        else:
            name = "{} * {}".format(multiplier, loss.__name__)
        super().__init__(name=name)
        self.loss = loss
        self.multiplier = multiplier

    def __call__(self, *inputs):
        return self.multiplier * self.loss.forward(*inputs)
class Activation(nn.Module):

    def __init__(self, name, **params):

        super().__init__()

        if name is None or name == 'identity':
            self.activation = nn.Identity(**params)
        elif name == 'sigmoid':
            self.activation = nn.Sigmoid()
        elif name == 'softmax2d':
            self.activation = nn.Softmax(dim=1, **params)
        elif name == 'softmax':
            self.activation = nn.Softmax(**params)
        elif name == 'logsoftmax':
            self.activation = nn.LogSoftmax(**params)
        elif name == 'argmax':
            self.activation = ArgMax(**params)
        elif name == 'argmax2d':
            self.activation = ArgMax(dim=1, **params)
        elif callable(name):
            self.activation = name(**params)
        else:
            raise ValueError('Activation should be callable/sigmoid/softmax/logsoftmax/None; got {}'.format(name))

    def forward(self, x):
        return self.activation(x)

import torch


def _take_channels(*xs, ignore_channels=None):
    if ignore_channels is None:
        return xs
    else:
        channels = [channel for channel in range(xs[0].shape[1]) if channel not in ignore_channels]
        xs = [torch.index_select(x, dim=1, index=torch.tensor(channels).to(x.device)) for x in xs]
        return xs


def _threshold(x, threshold=None):
    if threshold is not None:
        return (x > threshold).type(x.dtype)
    else:
        return x


def iou(pr, gt, eps=1e-7, threshold=None, ignore_channels=None):
    """Calculate Intersection over Union between ground truth and prediction
    Args:
        pr (torch.Tensor): predicted tensor
        gt (torch.Tensor):  ground truth tensor
        eps (float): epsilon to avoid zero division
        threshold: threshold for outputs binarization
    Returns:
        float: IoU (Jaccard) score
    """

    pr = _threshold(pr, threshold=threshold)
    pr, gt = _take_channels(pr, gt, ignore_channels=ignore_channels)

    intersection = torch.sum(gt * pr)
    union = torch.sum(gt) + torch.sum(pr) - intersection + eps
    return (intersection + eps) / union


jaccard = iou


def f_score(pr, gt, beta=1, eps=1e-7, threshold=None, ignore_channels=None):
    """Calculate F-score between ground truth and prediction
    Args:
        pr (torch.Tensor): predicted tensor
        gt (torch.Tensor):  ground truth tensor
        beta (float): positive constant
        eps (float): epsilon to avoid zero division
        threshold: threshold for outputs binarization
    Returns:
        float: F score
    """

    pr = _threshold(pr, threshold=threshold)
    pr, gt = _take_channels(pr, gt, ignore_channels=ignore_channels)

    tp = torch.sum(gt * pr)
    fp = torch.sum(pr) - tp
    fn = torch.sum(gt) - tp

    score = ((1 + beta ** 2) * tp + eps) / ((1 + beta ** 2) * tp + beta ** 2 * fn + fp + eps)

    return score


def accuracy(pr, gt, threshold=0.5, ignore_channels=None):
    """Calculate accuracy score between ground truth and prediction
    Args:
        pr (torch.Tensor): predicted tensor
        gt (torch.Tensor):  ground truth tensor
        eps (float): epsilon to avoid zero division
        threshold: threshold for outputs binarization
    Returns:
        float: precision score
    """
    pr = _threshold(pr, threshold=threshold)
    pr, gt = _take_channels(pr, gt, ignore_channels=ignore_channels)

    tp = torch.sum(gt == pr, dtype=pr.dtype)
    score = tp / gt.view(-1).shape[0]
    return score


def precision(pr, gt, eps=1e-7, threshold=None, ignore_channels=None):
    """Calculate precision score between ground truth and prediction
    Args:
        pr (torch.Tensor): predicted tensor
        gt (torch.Tensor):  ground truth tensor
        eps (float): epsilon to avoid zero division
        threshold: threshold for outputs binarization
    Returns:
        float: precision score
    """

    pr = _threshold(pr, threshold=threshold)
    pr, gt = _take_channels(pr, gt, ignore_channels=ignore_channels)

    tp = torch.sum(gt * pr)
    fp = torch.sum(pr) - tp

    score = (tp + eps) / (tp + fp + eps)

    return score


def recall(pr, gt, eps=1e-7, threshold=None, ignore_channels=None):
    """Calculate Recall between ground truth and prediction
    Args:
        pr (torch.Tensor): A list of predicted elements
        gt (torch.Tensor):  A list of elements that are to be predicted
        eps (float): epsilon to avoid zero division
        threshold: threshold for outputs binarization
    Returns:
        float: recall score
    """

    pr = _threshold(pr, threshold=threshold)
    pr, gt = _take_channels(pr, gt, ignore_channels=ignore_channels)

    tp = torch.sum(gt * pr)
    fn = torch.sum(gt) - tp

    score = (tp + eps) / (tp + fn + eps)

    return score

import torch.nn as nn

class JaccardLoss(Loss):
    def __init__(self, eps=1.0, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return 1 - jaccard(
            y_pr,
            y_gt,
            eps=self.eps,
            threshold=None,
            ignore_channels=self.ignore_channels,
        )


class DiceLoss(Loss):
    def __init__(self, eps=1.0, beta=1.0, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.beta = beta
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return 1 - f_score(
            y_pr,
            y_gt,
            beta=self.beta,
            eps=self.eps,
            threshold=None,
            ignore_channels=self.ignore_channels,
        )


class L1Loss(nn.L1Loss, Loss):
    pass


class MSELoss(nn.MSELoss, Loss):
    pass


class CrossEntropyLoss(nn.CrossEntropyLoss, Loss):
    pass


class NLLLoss(nn.NLLLoss, Loss):
    pass


class BCELoss(nn.BCELoss, Loss):
    pass


class BCEWithLogitsLoss(nn.BCEWithLogitsLoss, Loss):
    pass

class IoU(Metric):
    __name__ = "iou_score"

    def __init__(self, eps=1e-7, threshold=0.5, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.threshold = threshold
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return iou(
            y_pr,
            y_gt,
            eps=self.eps,
            threshold=self.threshold,
            ignore_channels=self.ignore_channels,
        )


class Fscore(Metric):
    def __init__(self, beta=1, eps=1e-7, threshold=0.5, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.beta = beta
        self.threshold = threshold
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return f_score(
            y_pr,
            y_gt,
            eps=self.eps,
            beta=self.beta,
            threshold=self.threshold,
            ignore_channels=self.ignore_channels,
        )


class Accuracy(Metric):
    def __init__(self, threshold=0.5, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.threshold = threshold
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return accuracy(
            y_pr,
            y_gt,
            threshold=self.threshold,
            ignore_channels=self.ignore_channels,
        )


class Recall(Metric):
    def __init__(self, eps=1e-7, threshold=0.5, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.threshold = threshold
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return recall(
            y_pr,
            y_gt,
            eps=self.eps,
            threshold=self.threshold,
            ignore_channels=self.ignore_channels,
        )


class Precision(Metric):
    def __init__(self, eps=1e-7, threshold=0.5, activation=None, ignore_channels=None, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.threshold = threshold
        self.activation = Activation(activation)
        self.ignore_channels = ignore_channels

    def forward(self, y_pr, y_gt):
        y_pr = self.activation(y_pr)
        return precision(
            y_pr,
            y_gt,
            eps=self.eps,
            threshold=self.threshold,
            ignore_channels=self.ignore_channels,
        )


metrics = [
    IoU(threshold=0.5),
    Accuracy(threshold=0.5),
    Fscore(threshold=0.5),
    Recall(threshold=0.5),
    Precision(threshold=0.5),
]

import torch
!pip install segmentation_models_pytorch
import segmentation_models_pytorch as smp

ENCODER = 'resnet50'
ENCODER_WEIGHTS = 'imagenet'
ACTIVATION = 'softmax'

model = smp.UnetPlusPlus(
    encoder_name = ENCODER,
    encoder_weights = ENCODER_WEIGHTS,
    classes = len(CLASSES),
    activation = ACTIVATION,
)
preprocessing_fn  = smp.encoders.get_preprocessing_fn(ENCODER, ENCODER_WEIGHTS)



print(model)





import torch.optim as optim
optimizer = torch.optim.Adam([
    dict(params = model.parameters(), lr = 0.0001)
])

loss = DiceLoss()



from torch.utils.data import DataLoader

train_dataset = Dataset(
    train_data,
    images_dir,
    augmentation=get_training_augmentation(),
    preprocessing=get_preprocessing(preprocessing_fn),
    classes=CLASSES,
)

valid_dataset = Dataset(
    validation_data,
    images_dir,
    augmentation=get_validation_augmentation(),
    preprocessing=get_preprocessing(preprocessing_fn),
    classes=CLASSES,
)

train_loader = DataLoader(train_dataset, batch_size=6, shuffle=True, num_workers=8)
valid_loader = DataLoader(valid_dataset, batch_size=1, shuffle=False, num_workers=7)


"""**Model Training**"""

import numpy as np


class Meter(object):
    """Meters provide a way to keep track of important statistics in an online manner.
    This class is abstract, but provides a standard interface for all meters to follow.
    """

    def reset(self):
        """Reset the meter to default settings."""
        pass

    def add(self, value):
        """Log a new value to the meter
        Args:
            value: Next result to include.
        """
        pass

    def value(self):
        """Get the value of the meter in the current state."""
        pass


class AverageValueMeter(Meter):
    def __init__(self):
        super(AverageValueMeter, self).__init__()
        self.reset()
        self.val = 0

    def add(self, value, n=1):
        self.val = value
        self.sum += value
        self.var += value * value
        self.n += n

        if self.n == 0:
            self.mean, self.std = np.nan, np.nan
        elif self.n == 1:
            self.mean = 0.0 + self.sum  # This is to force a copy in torch/numpy
            self.std = np.inf
            self.mean_old = self.mean
            self.m_s = 0.0
        else:
            self.mean = self.mean_old + (value - n * self.mean_old) / float(self.n)
            self.m_s += (value - self.mean_old) * (value - self.mean)
            self.mean_old = self.mean
            self.std = np.sqrt(self.m_s / (self.n - 1.0))

    def value(self):
        return self.mean, self.std

    def reset(self):
        self.n = 0
        self.sum = 0.0
        self.var = 0.0
        self.val = 0.0
        self.mean = np.nan
        self.mean_old = 0.0
        self.m_s = 0.0
        self.std = np.nan

import sys
import torch
from tqdm import tqdm as tqdm

class Epoch:
    def __init__(self, model, loss, metrics, stage_name, device="cpu", verbose=True):
        self.model = model
        self.loss = loss
        self.metrics = metrics
        self.stage_name = stage_name
        self.verbose = verbose
        self.device = device

        self._to_device()

    def _to_device(self):
        self.model.to(self.device)
        self.loss.to(self.device)
        for metric in self.metrics:
            metric.to(self.device)

    def _format_logs(self, logs):
        str_logs = ["{} - {:.4}".format(k, v) for k, v in logs.items()]
        s = ", ".join(str_logs)
        return s

    def batch_update(self, x, y):
        raise NotImplementedError

    def on_epoch_start(self):
        pass

    def run(self, dataloader):

        self.on_epoch_start()

        logs = {}
        loss_meter = AverageValueMeter()
        metrics_meters = {metric.__name__: AverageValueMeter() for metric in self.metrics}

        with tqdm(
            dataloader,
            desc=self.stage_name,
            file=sys.stdout,
            disable=not (self.verbose),
        ) as iterator:
            for x, y in iterator:
                x, y = x.to(self.device), y.to(self.device)
                loss, y_pred = self.batch_update(x, y)

                # update loss logs
                loss_value = loss.cpu().detach().numpy()
                loss_meter.add(loss_value)
                loss_logs = {self.loss.__name__: loss_meter.mean}
                logs.update(loss_logs)

                # update metrics logs
                for metric_fn in self.metrics:
                    metric_value = metric_fn(y_pred, y).cpu().detach().numpy()
                    metrics_meters[metric_fn.__name__].add(metric_value)
                metrics_logs = {k: v.mean for k, v in metrics_meters.items()}
                logs.update(metrics_logs)

                if self.verbose:
                    s = self._format_logs(logs)
                    iterator.set_postfix_str(s)

        return logs


class TrainEpoch(Epoch):
    def __init__(self, model, loss, metrics, optimizer, device="cpu", verbose=True):
        super().__init__(
            model=model,
            loss=loss,
            metrics=metrics,
            stage_name="train",
            device=device,
            verbose=verbose,
        )
        self.optimizer = optimizer

    def on_epoch_start(self):
        self.model.train()

    def batch_update(self, x, y):
        self.optimizer.zero_grad()
        prediction = self.model.forward(x)
        loss = self.loss(prediction, y)
        loss.backward()
        self.optimizer.step()
        return loss, prediction


class ValidEpoch(Epoch):
    def __init__(self, model, loss, metrics, device="cpu", verbose=True):
        super().__init__(
            model=model,
            loss=loss,
            metrics=metrics,
            stage_name="valid",
            device=device,
            verbose=verbose,
        )

    def on_epoch_start(self):
        self.model.eval()

    def batch_update(self, x, y):
        with torch.no_grad():
            prediction = self.model.forward(x)
            loss = self.loss(prediction, y)
        return loss, prediction


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

train_epoch = TrainEpoch(
    model,
    loss=loss,
    metrics=metrics,
    optimizer=optimizer,
    device=DEVICE,
    verbose=True,
)

valid_epoch = ValidEpoch(
    model,
    loss=loss,
    metrics=metrics,
    device=DEVICE,
    verbose=True,
)


max_score = 0

for i in range(0, 500):

    print('\nEpoch: {}'.format(i))
    train_logs = train_epoch.run(train_loader)
    valid_logs = valid_epoch.run(valid_loader)

    # Save the model with best iou score
    if max_score < valid_logs['iou_score']:
        max_score = valid_logs['iou_score']
        torch.save(model, "/content/drive/My Drive/UnetPlus.pth")
        print('Model saved!')

    if i == 50:
        optimizer.param_groups[0]['lr'] = 1e-5
        print('Decrease decoder learning rate to 1e-5!')





pip install nvidia

print(combined_train_dataset.columns)
print(combined_train_dataset.head())

Trained_model = torch.load("/content/drive/My Drive/UnetPlus.pth", map_location = torch.device('cpu'))

from torch.utils.data import DataLoader

DataLoader (
    dataset,
    batch_size = 8,
    shuffle = False,
    num_workers = 9,
    collate_fn = None,
    pin_memory = False
)

test_dataset = Dataset(
    test_data,
    images_dir,
    augmentation = None,
    preprocessing = get_preprocessing(preprocessing_fn),
    classes = CLASSES,
)

test_Dataloader = DataLoader(test_dataset)

metrics = [
    IoU(threshold = 0.5),
    Accuracy(threshold = 0.5),
    Fscore(threshold = 0.5),
    Recall(threshold = 0.5),
    Precision(threshold = 0.5),
]

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

test_epoch = ValidEpoch (
    model = Trained_model,
    loss = loss,
    metrics = metrics,
    device = DEVICE,
)
logs = test_epoch.run(test_Dataloader)
torch.save(model, "/content/drive/My Drive/test")

import matplotlib.pyplot as plt
import numpy as np
import torch


def visualize(image, ground_truth_mask, predicted_mask):
    """
    Visualize the input image, ground truth mask, and predicted mask.

    Parameters:
    - image: The input image as a NumPy array.
    - ground_truth_mask: The ground truth mask as a NumPy array.
    - predicted_mask: The predicted mask as a NumPy array.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Squeeze the first dimension if it has size 1
    image = np.squeeze(image)

    # Plot the image
    if len(image.shape) == 2:
        axes[0].imshow(image, cmap='gray')  # for grayscale images
    elif len(image.shape) == 3:
        if image.shape[0] == 1:
            image = np.squeeze(image, axis=0)  # handle single-channel images
            axes[0].imshow(image, cmap='gray')
        else:
            axes[0].imshow(image)  # for RGB images
    else:
        raise ValueError(f"Invalid shape {image.shape} for image data")

    axes[0].set_title('Image')
    axes[0].axis('off')

    # Plot the ground truth mask
    if len(ground_truth_mask.shape) == 0:  # Check if ground_truth_mask is a scalar
        ground_truth_mask = np.array([[ground_truth_mask]])  # Convert to NumPy array with shape (1, 1)
    axes[1].imshow(ground_truth_mask, cmap='viridis')
    axes[1].set_title('Ground Truth Mask')
    axes[1].axis('off')

    # Plot the predicted mask
    axes[2].imshow(predicted_mask, cmap='viridis')
    axes[2].set_title('Predicted Mask')
    axes[2].axis('off')

    plt.show()

import matplotlib.pyplot as plt
import numpy as np
import torch
import cv2

import matplotlib.pyplot as plt
import numpy as np
import torch
import cv2

# Define your DEVICE and Trained_model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Assuming Trained_model is your trained model

# Assuming CLASSES is a list of class names corresponding to your segmentation task

# Function to draw rectangles around regions based on predicted mask
def draw_rectangles(image, predicted_mask, class_index, confidence_threshold=0.5, threshold_area=400):
    # Apply thresholding to create a binary mask
    _, binary_mask = cv2.threshold(predicted_mask, confidence_threshold, 1, cv2.THRESH_BINARY)

    # Find contours in the binary mask
    contours, _ = cv2.findContours(binary_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw rectangles based on contours
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > threshold_area:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), color=(0, 255, 0), thickness=2)
            cv2.putText(image, CLASSES[class_index], (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Assuming test_dataset is your DataLoader
for i, (image, gt_mask) in enumerate(test_dataset):
    x_tensor = torch.from_numpy(image).to(DEVICE).unsqueeze(0)
    predicted_mask = Trained_model.predict(x_tensor)
    pr_mask = (predicted_mask.squeeze().cpu().numpy().round())
    pr_mask = pr_mask[1, :, :]
    gt_mask = np.squeeze(gt_mask)
    image_t = image.transpose(1, 2, 0)

    # Draw rectangles around regions based on predicted mask
    image_with_rectangles = image_t.copy()
    draw_rectangles(image_with_rectangles, pr_mask, class_index=1)

    # Visualize the image with rectangles, ground truth mask, and predicted mask
    visualize(
        image=image_with_rectangles,
        predicted_mask=pr_mask
    )

    # Convert the predicted mask to numpy and get the predicted class indices
    # predicted_output = torch.argmax(predicted_mask.squeeze(), dim=0).detach().cpu().numpy()
    Indices = np.unique(predicted_output)

    for i in Indices:
        print(CLASSES[i])

import cv2
import matplotlib.pyplot as plt
import numpy as np

def decode_segmentation_map(image, classesLength=2):
    Class_label_colors = np.array([
        # Background,
        (200, 200, 0), (20, 200, 0)  # Increased intensity of yellow color
    ])
    r = np.zeros_like(image).astype(np.uint8)
    g = np.zeros_like(image).astype(np.uint8)
    for l in range(0, classesLength):
        idx = image == l
        r[idx] = Class_label_colors[l, 1]
        g[idx] = Class_label_colors[l, 0]

    rgb = np.stack([r, g, np.zeros_like(r)], axis=2)  # Add a third channel with zeros
    return rgb

rgb_map = decode_segmentation_map(predicted_output, 2)
plt.imshow(rgb_map)
plt.show()

# Convert RGB to BGR for OpenCV
bgr_map = cv2.cvtColor(rgb_map, cv2.COLOR_RGB2BGR)
cv2.imwrite('/content/drive/My Drive/rgb_predicted_map.png', bgr_map)
