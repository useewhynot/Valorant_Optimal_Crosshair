import os
import cv2
import click
import matplotlib

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image


# load the video into an iterator because I don't have 100TB of RAM
# credit: https://vuamitom.github.io/2019/12/13/fast-iterate-through-video-frames.html
def get_video_iterator(vid_path: str, sample_rate: int = 1):
    data_stream = cv2.VideoCapture(vid_path)
    success = data_stream.grab()

    i = 0
    while success:
        if i % sample_rate == 0:
            _, img = data_stream.retrieve()
            yield cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        success = data_stream.grab()
    

# this is very good code I totally didn't steal from stackoverflow wdymmmmm
# credit https://stackoverflow.com/a/61730849
def get_dominant_color(img, palette_size=16, bounding_box: list = [340, 740, 665, 1160]):
    # crop ROI from image
    y0, x0, y1, x1 = bounding_box
    img = img[y0:y1, x0:x1]

    # convert numpy array to PIL image for black magic
    pil_img = Image.fromarray(img)
    # Resize image to speed up processing
    img = pil_img.copy()
    img.thumbnail((100, 100))

    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)

    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)
    palette_index = color_counts[0][1]
    dominant_color = palette[palette_index*3:palette_index*3+3]

    return dominant_color, 1


# gets average dominant color for the entire video/map
def get_vid_rgb_average(vid_iterator, vid_sum: np.ndarray = np.zeros(3), vid_count: int = 0, return_avg_state: bool = False):
    for img in vid_iterator:
        img_sum, img_count = get_dominant_color(img)
        vid_sum += img_sum
        vid_count += img_count
    vid_avg = vid_sum / vid_count
    if return_avg_state:
        return vid_avg, vid_sum, vid_count
    return vid_avg


def get_optimal_color(img_color: np.ndarray):
    # invert color and switch to HSV space
    raw_cross_color = (255 - img_color) / 255.0
    hsv_color = matplotlib.colors.rgb_to_hsv(raw_cross_color)

    # maximize saturation and value
    hsv_color[1:] = 1
    cross_color = matplotlib.colors.hsv_to_rgb(hsv_color)
    return matplotlib.colors.rgb2hex(cross_color)

@click.command()
@click.argument("vidpath")
@click.option("--sample-rate", default=1, help='number of frames between samples')
def main(vidpath: str, sample_rate: int):
    # get all eligible videos to consider
    cwd = os.getcwd()
    if os.path.isdir(vidpath):
        # this is a monstrosity
        vid_paths = [os.path.join(vidpath, f) for f in os.listdir(vidpath) 
                        if os.path.isfile(os.path.join(cwd, vidpath, f))]
    else:
        vid_paths = [vidpath]

    # average all the average RGB averages, this is not technically an average
    # NOTE: The reason why this is not technically an average is to give each 
    # map an equal weighting in the average, otherwise map videos with longer lengths
    # will have more weight in the average, and therefore bias the crosshair to that map.
    # Turns out laziness and terrible stats does have an upside lmfao
    data_avg = np.zeros(3)
    for path in vid_paths:
        vid_iter = get_video_iterator(path, sample_rate=sample_rate)
        vid_avg = get_vid_rgb_average(vid_iter)
        data_avg += vid_avg

    data_avg /= len(vidpath)
    cross_color = get_optimal_color(data_avg)
    click.echo(f"Optimal Crosshair Color: {cross_color}")

if __name__ == "__main__":
    main()