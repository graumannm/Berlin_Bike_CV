import os
from PIL import Image, ImageMath
import numpy as np
import torch
from torchvision import transforms
from torchvision.datasets import ImageFolder

import matplotlib.pyplot as plt


class MaskedDataset(ImageFolder):
    # use "train", "test", "mask" folder inside root_dir
    # mask is a segmentation mask with bikelane = 7
    # alpha defines how intensive the background should be: 1=original, 0=no background
    def __init__(
        self,
        root_dir,
        image_sub_dir,
        mask_sub_dir="mask",
        alpha=0.5,
        reduced_channel=True,
        transform=None,
    ):
        super().__init__(root=os.path.join(root_dir, image_sub_dir))
        self.mask_dir = os.path.join(root_dir, mask_sub_dir)
        self.alpha = alpha
        self.transform = transform
        self.reduced_channel = reduced_channel

    def __getitem__(self, index):
        img_path, label = self.imgs[index]
        img_base_name = os.path.splitext(os.path.basename(img_path))[0]
        mask_path = os.path.join(self.mask_dir, img_base_name + "_mask.png")
        image = Image.open(img_path)
        image = image.convert("RGBA")
        mask = Image.open(mask_path)
        # transform to array, PIL Image cannot be used to compare to 7 = bikelane
        mask = np.array(mask)
        blend_mask = np.ones_like(mask, dtype="float32") * 255
        blend_mask[mask != 7] *= self.alpha
        alpha_image = Image.fromarray(blend_mask.astype(np.uint8), mode="L")
        image.putalpha(alpha_image)

        # squeeze to 3-Channel image again
        if self.reduced_channel:
            r, g, b, a = image.split()
            # Multiplizieren der RGB-Kanäle mit dem Alpha-Kanal
            r = ImageMath.eval("convert(r * a / 255, 'L')", r=r, a=a)
            g = ImageMath.eval("convert(g * a / 255, 'L')", g=g, a=a)
            b = ImageMath.eval("convert(b * a / 255, 'L')", b=b, a=a)
            # Zusammenführen der Kanäle zu einem neuen Bild im RGB-Format
            image = Image.merge("RGB", (r, g, b))

        if self.transform is not None:
            image = self.transform(image)

        return image, label


# train_data = MaskedDataset(
#     "/Users/edith/DSR/git/portfolio_project/Torstr_Schoenhauser_2",
#     "train",
#     transform=transforms.ToTensor(),
#     alpha=0.2,
# )
# trainloader = torch.utils.data.DataLoader(train_data, batch_size=6, shuffle=True)


# def imshow(image, ax=None, title=None, normalize=True):
#     """Imshow for Tensor."""
#     if ax is None:
#         fig, ax = plt.subplots()
#     image = image.numpy().transpose((1, 2, 0))

#     if normalize:
#         mean = np.array([0.485, 0.456, 0.406])
#         std = np.array([0.229, 0.224, 0.225])
#         image = std * image + mean
#         image = np.clip(image, 0, 1)

#     ax.imshow(image)
#     ax.spines["top"].set_visible(False)
#     ax.spines["right"].set_visible(False)
#     ax.spines["left"].set_visible(False)
#     ax.spines["bottom"].set_visible(False)
#     ax.tick_params(axis="both", length=0)
#     ax.set_xticklabels("")
#     ax.set_yticklabels("")

#     return ax


# # Run this to test your data loader

# data_iter = iter(trainloader)

# images, labels = next(data_iter)
# fig, axes = plt.subplots(figsize=(20, 15), ncols=6)
# for ii in range(6):
#     ax = axes[ii]
#     imshow(images[ii], ax=ax, normalize=True)
