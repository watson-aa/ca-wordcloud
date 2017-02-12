import dropbox_download
import pdf_extract
from wordcloud import WordCloud
from PIL import Image
from nose.tools import assert_equal
import argparse

def prep_args():
    parser = argparse.ArgumentParser(description='Pull Consumer Affairs DigiTech PDFs from Dropbox and build a word cloud image.')
    parser.add_argument('-k', '--key', action='store', dest='api_key', type=str, help='Dropbox API key', required=True)
    parser.add_argument('-d', '--dimensions', action='store', dest='dimensions', type=str, default='800,600', help='Image dimensions (default: 800,600)')
    parser.add_argument('-f', '--font', action='store', dest='font', type=str, default='./Qraxy.ttf', help='Font family (default: Qraxy.ttf)')
    return parser.parse_args()

def write_cloud(args, text, filename):
    wc = WordCloud()
    dimensions = args.dimensions.split(',')

    if all(dimension.isdigit() for dimension in dimensions):
        wc.width = int(dimensions[0])
        wc.height = int(dimensions[1])
    wc.font_path = args.font
    wc.generate(text)

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

    write_cloud(args, cloud_text, 'cloud.png')

args = prep_args()
main(args)
