# Bike Map: Using Computer Vision for Bike Trip Routing

![graph_full_map_plus_route](https://github.com/graumannm/Berlin_Bike_CV/assets/130439108/8e64816f-ee14-423d-9bcf-8ad6350c7c11)

## About the project
We wanted to build a tool that optimises cycling around Berlin by avoiding cobblestones and giving preference to safe bike paths. We do this by using up-to-date street view images of Berlin from [Mapillary.com](https://www.mapillary.com/) to classify streets based on their surface and safety. 

## Background
Cycling is one of the most popular forms of transport in the city, however, there are over [6,000 reported bicycle accidents](https://www.berlin.de/en/news/7311434-5559700-fewer-bicycle-accidents-in-berlin.en.html#:~:text=About%206400%20bicycle%20accidents%20until,were%20about%207900%20accidents%20each.) every year. This excludes all minor, unreported accidents that people have every day. Berliners also battle daily with cobbled streets, which are uncomfortable and can be extremely dangerous in wet conditions. 
However, initiatives like pop-up bike lanes increased bicyle traffic by 25% since their introduction. Pop-up bike lanes are segregated cycle paths that often take the place of a lane of traffic and many such lanes have become permanent fixtures. Safety and comfort while riding a bike remain important factors for people, increasing both would see even more people cycling.

## Plan of action
We therefore set out to automate the detection of bike lanes and identification of road surfaces using computer vision models and classification. Using street view images from [Mapillary.com](https://www.mapillary.com/), we were able to access over 10 million recent pictures of Berlin (in lieu of Google street view images). 

## Happy cycling!

# Documentation

## Bike lane identification

The first step of our pipeline was to identify whether there was a bike lane present in any given image taken from Mapillary. We did this by performing semantic segmentation. We used a [Mask2Former vision transformer](https://huggingface.co/facebook/mask2former-swin-large-mapillary-vistas-semantic) that was pretrained on the [Mapillary Vistas dataset](https://www.mapillary.com/dataset/vistas).

## Safety labelling of bike lanes

Because bike lanes are visually diverse, we applied an unsupervised learning approach to cluster bike lane images based on their visual features in order to categorize them. Those clusters were then visually inspected and labelled based on what bike lanes they contained. Based on our clustering results, new bike lane images will be soft labelled by assigning them to the cluster to which (medoid) they have the highest cosine similarity.

The clustering is performed in 4 steps. 

1) Extraction of embeddings from [DINOv2 S14](https://github.com/facebookresearch/dinov2) in [s01_extract_embeddings.ipynb](https://github.com/graumannm/Berlin_Bike_CV/blob/main/s01_extract_embeddings.ipynb)
2) The elbow method is used to investigate the optimal number of clusters to explore in [s02_elbow_4_kmedoids.ipynb](https://github.com/graumannm/Berlin_Bike_CV/blob/main/s02_elbow_4_kmedoids.ipynb)
3) Perform k-medoids clustering with 2 clusters in [s03_kmedoids_clustering.ipynb](https://github.com/graumannm/Berlin_Bike_CV/blob/main/s03_kmedoids_clustering.ipynb)
4) Visualize the clustering results using t-SNE in [s04_tSNE_visualization.ipynb](https://github.com/graumannm/Berlin_Bike_CV/blob/main/s04_tSNE_visualization.ipynb)

## Road surface classification

If, however, no bike lane was initially detected, we would run the image through a small EfficientNetV2. We trained the model further on around 450 handlabelled images of both asphalt and cobblestone. The result was a model that gave us a binary output of either cobblestones or asphalt.

## Mapping and routing

Following this, we then had an output label for every road in Berlin. We then wanted to put this label onto a map with an assigned weight, according to the road surface and level of safety. This was achieved by converting an OSM map of berlin into a NetworkX graph and matching the coordinates of each label with the coordinates of each edge.
