import torch

a = torch.FloatTensor(2, 3)
b = torch.FloatTensor([2, 3, 4, 5])
a, b

##
import torch

a = torch.IntTensor(2, 3)
b = torch.IntTensor([2, 3, 4, 5])
a, b

##
import torch

a = torch.rand(2, 3)
a

##
import torch

a = torch.randn(2, 3)
a

##
import torch

a = torch.arange(1, 20, 2)
a

##
import torch

a = torch.zeros(2, 3)
a

##
import torch

a = torch.randn(2, 3)
b = torch.abs(a)
b

##
import torch

a = torch.randn(2, 3)
b = torch.randn(2, 3)
c = torch.add(a, b)
e = torch.add(c, 10)
c, e

##
a = torch.randn(2, 3)
b = torch.clamp(a, -0.1, 0.1)
a, b

##
a = torch.randn(2, 3)
b = torch.randn(2, 3)
c = torch.div(a, b)
a, b, c

##
a = torch.randn(2, 3)
b = torch.pow(a, 2)
a, b
##
a = torch.randn(2, 3)
b = torch.randn(2, 3)
c = torch.mm(a, b.T)
c
##
a = torch.randn(2, 3)
b = torch.randn(3)
c = torch.mv(a, b)
a, b, c
##
