# 这个脚本用于实现一个完整的神经网络
import torch
from torch.autograd import Variable

batch_n = 100  # 一个批次输入数据的数量
hidden_layer = 100
input_data = 1000  # 每个数据的特征为1000
output_data = 10

x = Variable(torch.randn(batch_n, input_data), requires_grad=False)
y = Variable(torch.randn(batch_n, output_data), requires_grad=False)
# 用Variable对Tensor数据类型变量进行封装的操作。requires_grad如果是False，表示该变量在进行自动梯度计算的过程中不会保留梯度值。
w1 = Variable(torch.randn(input_data, hidden_layer), requires_grad=True)
w2 = Variable(torch.randn(hidden_layer, output_data), requires_grad=True)

# 学习率和迭代次数
epoch_n = 50
lr = 1e-6

for epoch in range(epoch_n):
    h1 = x.mm(w1)  # (100,1000)*(1000,100)-->100*100
    print(h1.shape)
    h1 = h1.clamp(min=0)
    y_pred = h1.mm(w2)
    # y_pred = x.mm(w1).clamp(min=0).mm(w2)
    loss = (y_pred - y).pow(2).sum()
    print("epoch:{},loss:{:.4f}".format(epoch, loss.data))

    #     grad_y_pred = 2*(y_pred-y)
    #     grad_w2 = h1.t().mm(grad_y_pred)
    loss.backward()  # 后向传播
    #     grad_h = grad_y_pred.clone()
    #     grad_h = grad_h.mm(w2.t())
    #     grad_h.clamp_(min=0)#将小于0的值全部赋值为0，相当于sigmoid
    #     grad_w1 = x.t().mm(grad_h)
    w1.data -= lr * w1.grad.data
    w2.data -= lr * w2.grad.data

    w1.grad.data.zero_()
    w2.grad.data.zero_()

#     w1 = w1 -lr*grad_w1
#     w2 = w2 -lr*grad_w2

# %%
import torch
from torch.autograd import Variable

batch_n = 64  # 一个批次输入数据的数量
hidden_layer = 100
input_data = 1000  # 每个数据的特征为1000
output_data = 10


class Model(torch.nn.Module):  # 完成类继承的操作
    def __init__(self):
        super(Model, self).__init__()  # 类的初始化

    def forward(self, input, w1, w2):
        x = torch.mm(input, w1)
        x = torch.clamp(x, min=0)
        x = torch.mm(x, w2)
        return x

    def backward(self):
        pass


model = Model()
x = Variable(torch.randn(batch_n, input_data), requires_grad=False)
y = Variable(torch.randn(batch_n, output_data), requires_grad=False)
# 用Variable对Tensor数据类型变量进行封装的操作。requires_grad如果是F，表示该变量在进行自动梯度计算的过程中不会保留梯度值。
w1 = Variable(torch.randn(input_data, hidden_layer), requires_grad=True)
w2 = Variable(torch.randn(hidden_layer, output_data), requires_grad=True)

epoch_n = 30

for epoch in range(epoch_n):
    y_pred = model(x, w1, w2)

    loss = (y_pred - y).pow(2).sum()
    print("epoch:{},loss:{:.4f}".format(epoch, loss.data))
    loss.backward()
    w1.data -= lr * w1.grad.data
    w2.data -= lr * w2.grad.data

    w1.grad.data.zero_()
    w2.grad.data.zero_()

# %%
import torch
from torch.autograd import Variable

batch_n = 100  # 一个批次输入数据的数量
hidden_layer = 100
input_data = 1000  # 每个数据的特征为1000
output_data = 10

x = Variable(torch.randn(batch_n, input_data), requires_grad=False)
y = Variable(torch.randn(batch_n, output_data), requires_grad=False)
# 用Variable对Tensor数据类型变量进行封装的操作。requires_grad如果是F，表示该变量在进行自动梯度计算的过程中不会保留梯度值。

models = torch.nn.Sequential(
    torch.nn.Linear(input_data, hidden_layer),
    torch.nn.ReLU(),
    torch.nn.Linear(hidden_layer, output_data)
)
# torch.nn.Sequential括号内就是我们搭建的神经网络模型的具体结构，Linear完成从隐藏层到输出层的线性变换，再用ReLU激活函数激活
# torch.nn.Sequential类是torch.nn中的一种序列容器，通过在容器中嵌套各种实现神经网络模型的搭建，
# 最主要的是，参数会按照我们定义好的序列自动传递下去。

# %%
import torch
from torch.autograd import Variable

loss_f = torch.nn.MSELoss()
x = Variable(torch.randn(100, 100))
y = Variable(torch.randn(100, 100))
loss = loss_f(x, y)
loss.data
# tensor(1.9529)

# %%
import torch
from torch.autograd import Variable

loss_f = torch.nn.L1Loss()
x = Variable(torch.randn(100, 100))
y = Variable(torch.randn(100, 100))
loss = loss_f(x, y)
loss.data
# tensor(1.1356)

# %%
import torch
from torch.autograd import Variable

loss_f = torch.nn.CrossEntropyLoss()
x = Variable(torch.randn(3, 5))
y = Variable(torch.LongTensor(3).random_(5))  # 3个0-4的随机数字
loss = loss_f(x, y)
loss.data
# tensor(2.3413)

# %%
import torch
from torch.autograd import Variable
import torch
from torch.autograd import Variable

loss_fn = torch.nn.MSELoss()
x = Variable(torch.randn(100, 100))
y = Variable(torch.randn(100, 100))
loss = loss_fn(x, y)

batch_n = 100  # 一个批次输入数据的数量
hidden_layer = 100
input_data = 1000  # 每个数据的特征为1000
output_data = 10

x = Variable(torch.randn(batch_n, input_data), requires_grad=False)
y = Variable(torch.randn(batch_n, output_data), requires_grad=False)
# 用Variable对Tensor数据类型变量进行封装的操作。requires_grad如果是F，表示该变量在进行自动梯度计算的过程中不会保留梯度值。

models = torch.nn.Sequential(
    torch.nn.Linear(input_data, hidden_layer),
    torch.nn.ReLU(),
    torch.nn.Linear(hidden_layer, output_data)
)
# torch.nn.Sequential括号内就是我们搭建的神经网络模型的具体结构，Linear完成从隐藏层到输出层的线性变换，再用ReLU激活函数激活
# torch.nn.Sequential类是torch.nn中的一种序列容器，通过在容器中嵌套各种实现神经网络模型的搭建，
# 最主要的是，参数会按照我们定义好的序列自动传递下去。


for epoch in range(epoch_n):
    y_pred = models(x)

    loss = loss_fn(y_pred, y)
    if epoch % 1000 == 0:
        print("epoch:{},loss:{:.4f}".format(epoch, loss.data))
    models.zero_grad()

    loss.backward()

    for param in models.parameters():
        param.data -= param.grad.data * lr

# %%
import torch
from torch.autograd import Variable

batch_n = 100  # 一个批次输入数据的数量
hidden_layer = 100
input_data = 1000  # 每个数据的特征为1000
output_data = 10

x = Variable(torch.randn(batch_n, input_data), requires_grad=False)
y = Variable(torch.randn(batch_n, output_data), requires_grad=False)
# 用Variable对Tensor数据类型变量进行封装的操作。requires_grad如果是F，表示该变量在进行自动梯度计算的过程中不会保留梯度值。

models = torch.nn.Sequential(
    torch.nn.Linear(input_data, hidden_layer),
    torch.nn.ReLU(),
    torch.nn.Linear(hidden_layer, output_data)
)
# torch.nn.Sequential括号内就是我们搭建的神经网络模型的具体结构，Linear完成从隐藏层到输出层的线性变换，再用ReLU激活函数激活
# torch.nn.Sequential类是torch.nn中的一种序列容器，通过在容器中嵌套各种实现神经网络模型的搭建，
# 最主要的是，参数会按照我们定义好的序列自动传递下去。

# loss_fn = torch.nn.MSELoss()
# x = Variable(torch.randn(100,100))
# y = Variable(torch.randn(100,100))
# loss = loss_fn(x,y)

epoch_n = 300
lr = 1e-4
loss_fn = torch.nn.MSELoss()

optimzer = torch.optim.Adam(models.parameters(), lr=lr)
# 使用torch.optim.Adam类作为我们模型参数的优化函数，这里输入的是：被优化的参数和学习率的初始值。
# 因为我们需要优化的是模型中的全部参数，所以传递的参数是models.parameters()

# 进行，模型训练的代码如下：
for epoch in range(epoch_n):
    y_pred = models(x)
    loss = loss_fn(y_pred, y)
    print("Epoch:{},Loss:{:.4f}".format(epoch, loss.data))
    optimzer.zero_grad()  # 将模型参数的梯度归0

    loss.backward()
    optimzer.step()  # 使用计算得到的梯度值对各个节点的参数进行梯度更新。

# %%
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

data_train = datasets.MNIST(root="./data/",
                            transform=transform,
                            train=True,
                            download=True)
data_test = datasets.MNIST(root="./data/",
                           transform=transform,
                           train=False,
                           download=True)

# %%
import torchvision.models as models

resnet18 = models.resnet18()
alexnet = models.alexnet()
squeezenet = models.squeezenet1_0()
densenet = models.densenet_161()

# %%
import torchvision.models as models

resnet18 = models.resnet18(pretrained=True)
alexnet = models.alexnet(pretrained=True)

# %%
# torchvision.transforms: 常用的图片变换，例如裁剪、旋转等；
transform = transforms.Compose(
    [transforms.ToTensor(),  # 将PILImage转换为张量
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # 将[0, 1]归一化到[-1, 1]
     # 前面的（0.5，0.5，0.5） 是 R G B 三个通道上的均值， 后面(0.5, 0.5, 0.5)是三个通道的标准差
     ])
# 上述代码我们可以将transforms.Compose()看作一种容器，它能够同时对多种数据变换进行组合。
# 传入的参数是一个列表，列表中的元素就是对载入数据进行的变换操作。

# %%
import torch

data_loader_train = torch.utils.data.DataLoader(dataset=data_train,
                                                batch_size=64,  # 每个batch载入的图片数量，默认为1,这里设置为64
                                                shuffle=True,
                                                # num_workers=2#载入训练数据所需的子任务数
                                                )
data_loader_test = torch.utils.data.DataLoader(dataset=data_test,
                                               batch_size=64,
                                               shuffle=True)
# num_workers=2)

# %%
import torchvision
import matplotlib.pyplot as plt

# 预览
# 在尝试过多次之后，发现错误并不是这一句引发的，而是因为图片格式是灰度图只有一个channel，需要变成RGB图才可以，所以将其中一行做了修改：
images, labels = next(iter(data_loader_train))
# dataiter = iter(data_loader_train) #随机从训练数据中取一些数据
# images, labels = dater.next()

img = torchvision.utils.make_grid(images)

img = img.numpy().transpose(1, 2, 0)
std = [0.5, 0.5, 0.5]
mean = [0.5, 0.5, 0.5]
img = img * std + mean
print([labels[i] for i in range(64)])
plt.imshow(img)

# %%
import math
import torch
import torch.nn as nn


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

        # 构建卷积层之后的全连接层以及分类器
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(stride=2, kernel_size=2)
        )

        self.dense = torch.nn.Sequential(
            nn.Linear(14 * 14 * 128, 1024),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(1024, 10)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = x.view(-1, 14 * 14 * 128)
        x = self.dense(x)
        return x


model = Model()
cost = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters())
print(model)

# %%
from torch.autograd import Variable

n_epochs = 5

for epoch in range(n_epochs):
    running_loss = 0.0
    running_correct = 0
    print("Epoch {}/{}".format(epoch, n_epochs))
    print("-" * 10)
    for data in data_loader_train:
        X_train, y_train = data
        X_train, y_train = Variable(X_train), Variable(y_train)
        outputs = model(X_train)
        _, pred = torch.max(outputs.data, 1)
        optimizer.zero_grad()
        loss = cost(outputs, y_train)

        loss.backward()
        optimizer.step()
        running_loss += loss.data
        running_correct += torch.sum(pred == y_train.data)
    testing_correct = 0
    for data in data_loader_test:
        X_test, y_test = data
        X_test, y_test = Variable(X_test), Variable(y_test)
        outputs = model(X_test)
        _, pred = torch.max(outputs.data, 1)
        testing_correct += torch.sum(pred == y_test.data)
    print("Loss is:{:4f},Train Accuracy is:{:.4f}%,Test Accuracy is:{:.4f}".format(running_loss / len(data_train),
                                                                                   100 * running_correct / len(
                                                                                       data_train)
                                                                                   , 100 * testing_correct / len(
            data_test)))

# %%
data_loader_test = torch.utils.data.DataLoader(dataset=data_test,
                                               batch_size=4,
                                               shuffle=True)
X_test, y_test = next(iter(data_loader_test))
inputs = Variable(X_test)
pred = model(inputs)
_, pred = torch.max(pred, 1)

print("Predict Label is:", [i for i in pred.data])
print("Real Label is:", [i for i in y_test])
img = torchvision.utils.make_grid(X_test)
img = img.numpy().transpose(1, 2, 0)

std = [0.5, 0.5, 0.5]
mean = [0.5, 0.5, 0.5]
img = img * std + mean
plt.imshow(img)
# %%
import torch
import torchvision
from torchvision import datasets, transforms
from torch.autograd import Variable
import numpy as np
import matplotlib.pyplot as plt

# torchvision.transforms: 常用的图片变换，例如裁剪、旋转等；
# transform=transforms.Compose(
#     [transforms.ToTensor(),#将PILImage转换为张量
#      transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))#将[0, 1]归一化到[-1, 1]
#      #前面的（0.5，0.5，0.5） 是 R G B 三个通道上的均值， 后面(0.5, 0.5, 0.5)是三个通道的标准差
#     ])
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: x.repeat(3, 1, 1)),
    transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
])  # 修改的位置

data_train = datasets.MNIST(root="./data/",
                            transform=transform,
                            train=True,
                            download=True)
data_test = datasets.MNIST(root="./data/",
                           transform=transform,
                           train=False)

data_loader_train = torch.utils.data.DataLoader(dataset=data_train,
                                                batch_size=64,  # 每个batch载入的图片数量，默认为1,这里设置为64
                                                shuffle=True,
                                                # num_workers=2#载入训练数据所需的子任务数
                                                )
data_loader_test = torch.utils.data.DataLoader(dataset=data_test,
                                               batch_size=64,
                                               shuffle=True)
# num_workers=2)

# 预览
# 在尝试过多次之后，发现错误并不是这一句引发的，而是因为图片格式是灰度图只有一个channel，需要变成RGB图才可以，所以将其中一行做了修改：
images, labels = next(iter(data_loader_train))
# dataiter = iter(data_loader_train) #随机从训练数据中取一些数据
# images, labels = dataiter.next()

img = torchvision.utils.make_grid(images)

img = img.numpy().transpose(1, 2, 0)
std = [0.5, 0.5, 0.5]
mean = [0.5, 0.5, 0.5]
img = img * std + mean
print([labels[i] for i in range(64)])
plt.imshow(img)

import math
import torch
import torch.nn as nn
from tqdm import tqdm


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()

        # 构建卷积层之后的全连接层以及分类器
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(stride=2, kernel_size=2)
        )

        self.dense = torch.nn.Sequential(
            nn.Linear(14 * 14 * 128, 1024),
            nn.ReLU(),
            nn.Dropout(p=0.5),
            nn.Linear(1024, 10)
        )

    def forward(self, x):
        x = self.conv1(x)
        x = x.view(-1, 14 * 14 * 128)
        x = self.dense(x)
        return x


model = Model()
cost = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters())
print(model)

n_epochs = 5  # 这里的每批次数据进行5次迭代优化模型

for epoch in range(n_epochs):
    running_loss = 0.0
    running_correct = 0
    print("Epoch {}/{}".format(epoch, n_epochs))
    print("-" * 10)
    for data in tqdm(data_loader_train):  # 将数据加载器封装成tqdm对象
        X_train, y_train = data
        X_train, y_train = Variable(X_train), Variable(y_train)
        outputs = model(X_train)
        _, pred = torch.max(outputs.data, 1)
        optimizer.zero_grad()
        loss = cost(outputs, y_train)

        loss.backward()
        optimizer.step()
        running_loss += loss.data
        running_correct += torch.sum(pred == y_train.data)

    testing_correct = 0
    for data in tqdm(data_loader_test):
        X_test, y_test = data
        X_test, y_test = Variable(X_test), Variable(y_test)
        outputs = model(X_test)
        _, pred = torch.max(outputs.data, 1)
        testing_correct += torch.sum(pred == y_test.data)

    print("Loss is:{:4f},Train Accuracy is:{:.4f}%,Test Accuracy is:{:.4f}".format(running_loss / len(data_train),
                                                                                   100 * running_correct / len(
                                                                                       data_train),
                                                                                   100 * testing_correct / len(
                                                                                       data_test)))
# %%

data_loader_test = torch.utils.data.DataLoader(dataset=data_test,
                                               batch_size=4,
                                               shuffle=True)
X_test, y_test = next(iter(data_loader_test))
inputs = Variable(X_test)
pred = model(inputs)
_, pred = torch.max(pred, 1)

print("Predict Label is:", [i for i in pred.data])
print("Real Label is:", [i for i in y_test])
img = torchvision.utils.make_grid(X_test)
img = img.numpy().transpose(1, 2, 0)

std = [0.5, 0.5, 0.5]
mean = [0.5, 0.5, 0.5]
img = img * std + mean
plt.imshow(img)

# %%
import torch

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_network
# 到这个网站下载cuda Toolkit工具
# %%
