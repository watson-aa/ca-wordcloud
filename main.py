import dropbox_download
import pdf_extract
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
from nose.tools import assert_equal
import argparse
import numpy as np
from os import path

def prep_args():
    parser = argparse.ArgumentParser(description='Pull Consumer Affairs DigiTech PDFs from Dropbox and build a word cloud image.')
    parser.add_argument('-k', '--key', action='store', dest='api_key', type=str, help='Dropbox API key', required=True)
    parser.add_argument('-d', '--dimensions', action='store', dest='dimensions', type=str, default='800,600', help='Image dimensions (default: 800,600)')
    parser.add_argument('-f', '--font', action='store', dest='font', type=str, default='./Qraxy.ttf', help='Font family (default: Qraxy.ttf)')
    parser.add_argument('-fs', '--fontsize', action='store', dest='max_font_size', type=int, default=300, help='Maximum font size used in the cloud.')
    parser.add_argument('-m', '--mask', action='store', dest='mask', type=str, help='Image mask to use. Size will override dimensions parameters.')
    parser.add_argument('-c', '--colorize', action='store_true', dest='colorize', help='Use colors in the mask in the resulting cloud image.')
    parser.add_argument('-o', '--output', action='store', dest='filename', help='Destination filename for the cloud image.', required=True)
    parser.add_argument('-w', '--words', action='store', dest='max_words', type=int, default=125, help='Maximum number of words in the cloud.')
    return parser.parse_args()

def apply_dimensions(wc, dimensions):
    arr_dimensions = dimensions.split(',')

    if all(dimension.isdigit() for dimension in arr_dimensions):
        wc.width = int(arr_dimensions[0])
        wc.height = int(arr_dimensions[1])
    else:
        wc.width = 800
        wc.height = 600

def apply_mask(wc, mask_file):
    mask = np.array(Image.open(mask_file))
    wc.mask = mask
    wc.width = mask.shape[1]
    wc.height = mask.shape[0]
    return mask

def apply_colors(wc, mask):
    mask_colors = ImageColorGenerator(mask)
    wc.recolor(color_func=mask_colors)

def generate_cloud(args, text, filename):
    wc = WordCloud()

    apply_dimensions(wc, args.dimensions)

    wc.font_path = args.font
    wc.max_words = args.max_words

    if args.mask is not None:
        mask = apply_mask(wc, args.mask)

    wc.max_font_size = args.max_font_size

    wc.generate(text)

    if args.mask is not None and args.colorize:
        apply_colors(wc, mask)

    wc.to_file(filename)
    loaded_image = Image.open(filename)
    assert_equal(loaded_image.size, (wc.width, wc.height))

def main(args):
    dbd = dropbox_download.DBD(args.api_key)
    files = dbd.list_folder('/')
    cloud_text = ''

    for x, f in enumerate(files):
        data = dbd.download('/', f.name)
        text = pdf_extract.get_text(data)

        # weight more recent files
        for y in range(x+1):
            cloud_text = cloud_text + ' ' + text

    cloud_text = pdf_extract.combine_similar(cloud_text)

    generate_cloud(args, cloud_text, args.filename)

args = prep_args()
main(args)
