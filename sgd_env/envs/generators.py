from typing import Callable, Generator, Any, Iterator, Tuple

import torch
from torch import nn
import torch.nn.functional as F
from torchvision import datasets, transforms
import numpy as np


Epochs = int
Model = nn.Module
OptimizerParams = nn.Module
LossType = nn.Module

DataIterator = Iterator[Tuple[torch.Tensor, torch.Tensor]]
InstanceGenerator = Tuple[Model, OptimizerParams, LossType, DataIterator, Epochs]
InstanceGeneratorFunc = Callable[[torch.Generator, ...], InstanceGenerator]


def random_feature_extractor(rng, **kwargs):
    n_layers = rng.randint(low=2, high=5)
    use_dropout = rng.randint(low=0, high=2)
    use_pooling = rng.randint(low=0, high=2)
    in_size = 1
    layers = []
    for i in range(n_layers):
        out_size = rng.randint(low=16, high=129)
        layers.append(nn.Conv2d(in_size, out_size, 3, 1))
        if use_dropout:
            layers.append(nn.Dropout(rng.rand()))
        layers.append(nn.ReLU())
        in_size = out_size

    if use_pooling:
        layers.append(nn.MaxPool2d(rng.randint(low=2, high=5)))

    return nn.Sequential(*layers)


def random_mnist_model(rng, **kwargs):
    class MNISTModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.f = random_feature_extractor(rng)
            n_features = torch.prod(torch.tensor(self.f(torch.zeros((1, 1, 28,
                28))).shape))
            size = rng.randint(low=16, high=129)
            self.fc1 = nn.Linear(n_features, size)
            self.fc2 = nn.Linear(size, 10)

        def forward(self, x):
            x = self.f(x)
            x = torch.flatten(x, 1)
            x = self.fc1(x)
            x = F.relu(x)
            x = self.fc2(x)
            output = F.log_softmax(x, dim=1)
            return output

    return MNISTModel()


def random_mnist_loader(rng, **kwargs):
      transform=transforms.Compose([
          transforms.ToTensor(),
          transforms.Normalize((0.1307,), (0.3081,))
          ])
      train_kwargs = {'batch_size': kwargs['training_batch_size']}
      test_kwargs = {'batch_size': kwargs['validation_batch_size']}
      dataset1 = datasets.MNIST('data', train=True, download=True,
                         transform=transform)
      dataset2 = datasets.MNIST('data', train=False,
                         transform=transform)
      train_loader = torch.utils.data.DataLoader(dataset1,**train_kwargs)
      test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)
      return iter(train_loader), test_loader


def random_optimizer_parameters(rng, **kwargs):
    lr_low = np.log(kwargs['learning_rate_range'][0])
    lr_high = np.log(kwargs['learning_rate_range'][1])
    log_lr = (lr_low - lr_high) * rng.rand() + lr_high
    return {'lr': np.exp(log_lr)}


def random_mnist_instance(rng, **kwargs):
    model = random_mnist_model(rng, **kwargs)
    loaders = random_mnist_loader(rng, **kwargs)
    optimizer_params = random_optimizer_parameters(rng, **kwargs)
    loss = F.nll_loss
    epoch_low = kwargs['epoch_range'][0]
    epoch_high = kwargs['epoch_range'][1]
    epochs = rng.randint(low=epoch_low, high=epoch_high)
    return model, optimizer_params, loss, loaders, epochs


def random_instance(rng, **kwargs):
    print(kwargs)
    datasets = ['MNIST']
    idx = rng.randint(low=0, high=len(datasets))
    dataset = datasets[idx]
    if dataset == 'MNIST':
        instance = random_mnist_instance(rng, **kwargs)
    else:
        raise NotImplementedError
    return instance
