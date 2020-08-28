import os
import imageio
from matplotlib import pyplot as plt

import torch
from torch.nn import init
from torchvision.utils import save_image

from config import *

device = 'cuda' if torch.cuda.is_available() else 'cpu'


def make_dirs(path):
    """Make Directory If not Exists"""
    if not os.path.exists(path):
        os.makedirs(path)


def init_weights_normal(m):
    """Normal Weight Initialization"""
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        init.normal(m.weight.data, 0.0, 0.02)
    elif classname.find('Linear') != -1:
        init.normal(m.weight.data, 0.0, 0.02)


def init_weights_xavier(m):
    """Xavier Weight Initialization"""
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        init.xavier_normal(m.weight.data, gain=0.02)
    elif classname.find('Linear') != -1:
        init.xavier_normal(m.weight.data, gain=0.02)


def init_weights_kaiming(m):
    """Kaiming He Weight Initialization"""
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
    elif classname.find('Linear') != -1:
        init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')


def get_lr_scheduler(optimizer):
    """Learning Rate Scheduler"""
    if config.lr_scheduler == 'step':
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=config.lr_decay_every, gamma=config.lr_decay_rate)
    elif config.lr_scheduler == 'plateau':
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.2, threshold=0.01, patience=5)
    elif config.lr_scheduler == 'cosine':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.num_epochs, eta_min=0)
    else:
        raise NotImplementedError
    return scheduler


def set_requires_grad(networks, requires_grad=False):
    """Prevent a Network from Updating"""
    for network in networks:
        for param in network.parameters():
            param.requires_grad = requires_grad


def denorm(x):
    """De-normalization"""
    out = (x+1) / 2
    return out.clamp(0, 1)


def sample_images(horse_loader, zebra_loader, generator_1, generator_2, epoch, path):
    """Save Sample Images for Every Epoch"""
    horse = next(iter(horse_loader))
    zebra = next(iter(zebra_loader))

    real_A = horse.to(device)
    real_B = zebra.to(device)

    fake_B = generator_1(real_A)
    fake_A = generator_2(real_B)

    fake_ABA = generator_2(fake_B)
    fake_BAB = generator_1(fake_A)

    images = [real_A, fake_B, fake_ABA, real_B, fake_A, fake_BAB]

    result = torch.cat(images, dim=0)
    save_image(denorm(result.data),
               os.path.join(path, 'CycleGAN_Horse2Zebra_Epoch_%03d.png' % (epoch + 1)),
               nrow=6,
               normalize=True)

    del images


def plot_losses(discriminator_a_losses, discriminator_b_losses, generator_losses, num_epochs, path):
    """Plot Losses After Training"""
    plt.figure(figsize=(10, 5))
    plt.xlabel("Iterations")
    plt.ylabel("Losses")
    plt.title("CycleGAN Losses over Epoch {}".format(num_epochs))
    plt.plot(discriminator_a_losses, label='Discriminator A', alpha=0.5)
    plt.plot(discriminator_b_losses, label='Discriminator B', alpha=0.5)
    plt.plot(generator_losses, label='Generator', alpha=0.5)
    plt.legend(loc='best')
    plt.grid()
    plt.savefig(os.path.join(path, 'CycleGAN_Losses_Epoch_{}.png'.format(num_epochs)))


def make_gifs_train(title, path):
    """Create a GIF file After Train"""
    images = os.listdir(path)
    generated_images = []

    for i in range(len(images)):
        file = os.path.join(path, '%s_Horse2Zebra_Epoch_%03d.png' % (title, i+1))
        generated_images.append(imageio.imread(file))

    imageio.mimsave(path + '{}_Train_Results.gif'.format(title), generated_images, fps=2)
    print("{} gif file is generated.".format(title))


def make_gifs_test(title, direction, path):
    """Create a GIF file After Inference"""
    images = os.listdir(path)
    generated_images = []

    for i in range(len(images)):
        file = os.path.join(path, '%s_%s_Results_%03d.png' % (title, direction, i + 1))
        generated_images.append(imageio.imread(file))

    imageio.mimsave(path + '{}_{}_Test_Results.gif'.format(title, direction), generated_images, fps=2)
    print("{} gif file is generated.".format(title))