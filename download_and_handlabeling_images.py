

import mercantile, mapbox_vector_tile
import requests, json, os
from vt2geojson.tools import vt_bytes_to_geojson
import time
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageTk
import io
from dotenv import load_dotenv

### Define Bounding Box

# define bounding box in [west_lng,_south_lat,east_lng,north_lat] format
west, south, east, north = [
    13.353378064867647,
    52.52154344619529,
    13.374041076793597,
    52.5292240660736,
]


### Setup for image download

# Mapillary access token
load_dotenv()
access_token = os.getenv("MAPILLARY_TOKEN")

# vector tile endpoints
tile_coverage = "mly1_public"

# vector tile endpoint
tile_layer = "image"

# get the list of tiles intersecting the bounding box
tiles = list(mercantile.tiles(west, south, east, north, 14))


### Setup for saving images

# save in current folder
data_dir = "."

# create new image folder with timestamp
ts = time.time()
ts = str(ts)
ts = ts.split(".")[0]
new_image_dir = os.path.join(data_dir, ts)

# define classes
types = ["cobblestones", "road", "bikelane", "other"]

# create main folder
if not os.path.exists(new_image_dir):
    os.makedirs(new_image_dir)

# create subfolders for classes
for t in types:
    type_dir = os.path.join(new_image_dir, t)
    if not os.path.exists(type_dir):
        os.makedirs(type_dir)


### Definition of GUI for image labeling

discard = "DISCARD"
labels = types + [discard]


def label_image(image_name, image_url):
    def on_button_click(label):
        nonlocal root
        nonlocal image_name
        nonlocal image_data

        if labels[label] != discard:
            # rename labeled image
            labeled_filename = f"{labels[label]}_{str(image_name)}.jpg"
            labeled_path = os.path.join(new_image_dir, labels[label], labeled_filename)

            # save image
            with open(labeled_path, "wb") as handler:
                handler.write(image_data)

        # close GUI
        root.quit()

    # Initialze GUI
    root = tk.Tk()
    root.title("Labeling")

    image_data = requests.get(image_url, stream=True).content
    img = Image.open(io.BytesIO(image_data))
    img.thumbnail((600, 600))
    img_tk = ImageTk.PhotoImage(img)

    # Show image
    # TODO: define fixed position ob screen
    label = tk.Label(root, image=img_tk)
    label.pack()

    # Create labeling buttons
    for i, label_name in enumerate(labels):
        button = tk.Button(
            root, text=label_name, command=lambda i=i: on_button_click(i)
        )
        button.pack()

    root.mainloop()
    root.destroy()


### Download images and open GUI for labeling

# loop over list of tiles to get Mapillary endpoints data and make request
# reduce number of images by only taking every xth image
rate = 10

i = 0
for tile in tiles:
    tile_url = (
        "https://tiles.mapillary.com/maps/vtp/{}/2/{}/{}/{}?access_token={}".format(
            tile_coverage, tile.z, tile.x, tile.y, access_token
        )
    )
    response = requests.get(tile_url)
    data = vt_bytes_to_geojson(
        response.content, tile.x, tile.y, tile.z, layer=tile_layer
    )

    for feature in data["features"]:
        # avoid panorama pictures
        if feature["properties"]["is_pano"]:
            continue

        # get coordinates
        lng = feature["geometry"]["coordinates"][0]
        lat = feature["geometry"]["coordinates"][1]

        # ensure feature falls inside bounding box since tiles can extend beyond
        if lng > west and lng < east and lat > south and lat < north:
            i += 1

            if i % rate == 0:
                # request the URL of each image
                image_id = feature["properties"]["id"]
                header = {"Authorization": "OAuth {}".format(access_token)}
                # chose image size to download
                # thumb_256_url - string, URL to the 256px wide thumbnail.
                # thumb_1024_url - string, URL to the 1024px wide thumbnail.
                # thumb_2048_url - string, URL to the 2048px wide thumbnail.
                image_size = "thumb_1024_url"
                url = "https://graph.mapillary.com/{}?fields={}".format(
                    image_id, image_size
                )
                r = requests.get(url, headers=header)
                data = r.json()
                image_url = data[image_size]

                # open GUI for labeling:
                label_image(image_id, image_url)

print("Done.")
