import dropbox_download
import pdf_extract
from wordcloud import WordCloud
from PIL import Image
from nose.tools import assert_equal

files = dropbox_download.list_folder('/')
cloud_text = ''

def write_cloud(text, filename):
    wc = WordCloud()
    wc.width = 800
    wc.height = 600
    wc.font_path = '/Users/aaron/Library/Fonts/Qraxy.ttf'
    wc.generate(text)

    wc.to_file(filename)
    loaded_image = Image.open(filename)
    assert_equal(loaded_image.size, (wc.width, wc.height))

for x, f in enumerate(files):
    data = dropbox_download.download('/', f.name)
    text = pdf_extract.get_text(data)

    # weight more recent files
    for y in range(x+1):
        cloud_text = cloud_text + ' ' + text

cloud_text = pdf_extract.combine_similar(cloud_text)

write_cloud(cloud_text, 'foo.png')
