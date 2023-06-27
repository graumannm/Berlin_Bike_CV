# -*- coding: utf-8 -*-
"""Inference_with_Mask2Former.ipynb"""

from transformers import AutoImageProcessor, Mask2FormerForUniversalSegmentation
from torchvision.transforms import ToPILImage
import torch
from PIL import Image
import os
import random
import numpy as np
import matplotlib.pyplot as plt

random.seed(42)

processor = AutoImageProcessor.from_pretrained(
    "facebook/mask2former-swin-large-mapillary-vistas-semantic"
)
model = Mask2FormerForUniversalSegmentation.from_pretrained(
    "facebook/mask2former-swin-large-mapillary-vistas-semantic"
)

# # generate random color palette, which maps each class to a RGB value
# color_palette = [
#     list(np.random.choice(range(256), size=3))
#     for _ in range(len(model.config.id2label))
# ]

# create an instance of TorchToImage
torch_to_image = ToPILImage()

# import requests

# url = 'https://scontent-ber1-1.xx.fbcdn.net/m1/v/t6/An9uzB4ppevzT85qHHTZwEhpOhuz_r87F7l376L6b-eQKrl45EjO5N12Z06UfUEFEnWKOqsKMBNRdkONObe-iuE9yWoRf7IOYEdTuGPkV_qtJmWEq_t5re8u7c-37yFcCqCnOwulFvs3xxSg0u3kCg?stp=s2048x1536&ccb=10-5&oh=00_AfD4sIzpkC-kfX9wXmvk_45VGq4tUMvC153H7EpsV_9fYA&oe=64AFEF1B&_nc_sid=49dc0d'
# image = Image.open(requests.get(url, stream=True).raw)
# image

# Path to the directory containing the images
image_directory = "./Torstr_Schoenhauser_2"

# Get a list of all image files in the directory
image_files = [
    os.path.join(image_directory, file)
    for file in os.listdir(image_directory)
    if file.endswith((".jpg", ".jpeg", ".png"))
]

# Cycle through the images
for i, image_file in enumerate(image_files):
    i += 1
    if i > 100:
        break
    print(f"Masking image {i}...\n")

    # Load image
    image = Image.open(image_file)

    inputs = processor(images=image, return_tensors="pt")
    # for k,v in inputs.items():
    #   print(k,v.shape)

    # forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # you can pass them to processor for postprocessing
    predicted_map = processor.post_process_semantic_segmentation(
        outputs, target_sizes=[image.size[::-1]]
    )[0]
    predicted_map = predicted_map.to(torch.uint8)

    # color_seg = np.zeros(
    #     (predicted_map.shape[0], predicted_map.shape[1], 3), dtype=np.uint8
    # )  # height, width, 3
    # palette = np.array(color_palette)
    # for label, color in enumerate(palette):
    #     color_seg[predicted_map == label, :] = color
    # # Convert to BGR
    # color_seg = color_seg[..., ::-1]

    # Save image
    # mask = Image.fromarray(color_seg.astype(np.uint8))
    predicted_file = f"{os.path.basename(image_file).split('.')[0]}_mask.png"
    predicted_path = os.path.join(image_directory, predicted_file)
    # mask.save(predicted_path)
    pred_mask = torch_to_image(predicted_map)
    pred_mask.save(predicted_path)

    # # Show image + mask
    # img = np.array(image) * 0.5 + color_seg * 0.5
    # img = img.astype(np.uint8)

    # plt.figure(figsize=(15, 10))
    # plt.imshow(img)
    # plt.show()
