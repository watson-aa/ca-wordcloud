import PyPDF2
import re
import string
import enchant

def cleanse_common(text):
    # remove brand names
    arr_brands = ['stop&shop',
                  'stop & shop',
                  'stopandshop',
                  'stop and shop',
                  'S&S',
                  'Giant',
                  'Martins']
    re_brands = re.compile('(' + string.join(arr_brands, '|') + ')', re.IGNORECASE)

    return re_brands.sub(' ', text)

def cleanse_nonwords(text):
    d = enchant.Dict('en_US')
    out = ''
    for word in re.compile('\W+').split(text):
        if word != '' and d.check(word):
            out = out + ' ' + word
    return out

def cleanse(text):
    output = cleanse_common(text)
    output = cleanse_nonwords(output)
    return output

def get_text(data):
    pdfReader = PyPDF2.PdfFileReader(data)

    text = ''

    for page in pdfReader.pages:
        lines = re.split('\d{2}\/\d{2}\/\d{4}\d{2}:\d{2}:\d{9}', page.extractText())

        for line in lines:
            re_search = re.search('^([A-Z]{2})(\d{4})(.*)CUSTOMER COMMENTS: (.*)$', line)
            if re_search is not None and re_search.lastindex > 1:
                text = text + ' ' + re_search.group(4)

    return cleanse(text)

def combine_similar(text):
    endings = ('s', 'es', 'ed', 'ing')
    re_ending = re.compile('(.*)(' + '|'.join(endings) + ')$', re.IGNORECASE)
    words = []
    for word in re.compile('\W+').split(text):
        if word.endswith(endings):
            result = re_ending.match(word)
            if result is not None and result.group(1) in words:
                words.append(result.group(1))
            else:
                words.append(word)
        else:
            words.append(word)

    return ' '.join(words)
