import re
import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
from urllib import request

from wpreddit import config

# credit: http://www.techniqal.com/blog/2011/01/18/python-3-file-read-write-with-urllib/
# in - string - direct url of the image to download
# out - Image - image
# downloads the specified image and saves it to disk
def download_image(url, title):
    uaurl = request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script'})
    f = request.urlopen(uaurl, timeout=3)
    print("downloading " + url)
    try:
        img = Image.open(f)
        if config.resize:
            config.log("resizing the downloaded wallpaper")
            img = ImageOps.fit(img, (config.minwidth, config.minheight), Image.ANTIALIAS)
        if config.settitle:
            img = set_image_title(img, title)
        if config.opsys == "Windows":
            img.save(config.walldir + '\\wallpaper.bmp', "BMP")
        else:
            img.save(config.walldir + '/wallpaper.jpg', "JPEG")
    except IOError:
        print("Error saving image!")
        sys.exit(1)

def download_image_and_save(url, title):
    uaurl = request.Request(url, headers={'User-Agent': 'wallpaper-reddit python script'})
    f = request.urlopen(uaurl, timeout=3)
    print("downloading " + url)
    try:
        img = Image.open(f)
        # resize image if needed
        if config.resize:
            config.log("resizing the downloaded wallpaper")
            img = ImageOps.fit(img, (config.minwidth, config.minheight), Image.ANTIALIAS)
        if config.settitle:
            img = set_image_title(img, title)
        # create save path if needed
        if not os.path.exists(config.savedir):
            os.makedirs(config.savedir)
            config.log(config.savedir + " created")
        if not os.path.isfile(config.savedir + '/titles.txt'):
            with open(config.savedir + '/titles.txt', 'w') as f:
                f.write('Titles of the saved wallpapers:')
            config.log(config.savedir + "/titles.txt created")
        wpcount = 0
        path = ''
        # count images in dir, save as 'wallpaper' n+1
        if config.opsys == "Windows":
            path = config.savedir + ('\\wallpaper.bmp')
            while os.path.isfile(config.savedir + '\\wallpaper' + str(wpcount) + '.bmp'):
                wpcount += 1
            path = config.savedir + ('\\wallpaper' + str(wpcount) + '.bmp')
            img.save(path, 'BMP')
        else:
            path = config.savedir + ('/wallpaper.jpg')
            while os.path.isfile(config.savedir + '/wallpaper' + str(wpcount) + '.jpg'):
                wpcount += 1
            path = config.savedir + ('/wallpaper'  + str(wpcount) + '.jpg')
            img.save(path, 'JPEG')
        # write title of image to titles logging file
        with open(config.savedir + '/titles.txt', 'a') as f:
            f.write('\n' + 'wallpaper' + str(wpcount) + ': ' + title)
        print("Saved as \'wallpaper" + str(wpcount) + "\'")
        return True
    except IOError:
        print("Error saving image!")
    return False
    
# in - string, string - path of the image to set title on, title for image
def set_image_title(img, title):
    config.log("setting title")
    title = remove_tags(title)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(config.walldir + '/fonts/Cantarell-Regular.otf', size=config.titlesize)
    x = 0
    y = 0
    if config.titlealign_x == "left":
        x = config.titleoffset_x
    elif config.titlealign_x == "center":
        text_x = font.getsize(title)[0]
        x = (img.size[0] - text_x)/2
    elif config.titlealign_x == "right":
        text_x = font.getsize(title)[0]
        x = img.size[0] - text_x - config.titleoffset_x
    if config.titlealign_y == "top":
        y = config.titleoffset_y
    elif config.titlealign_y == "bottom":
        text_y = font.getsize(title)[1]
        y = img.size[1] - text_y - config.titleoffset_y
    # shadow = Image.new('RGBA', img.size, (255,255,255,0))
    # shadowdraw = ImageDraw.Draw(shadow)
    # shadowdraw.text((x+2, y+2), title, font=font, fill=(255,255,255))
    draw.text((x+2, y+2), title, font=font, fill=(0, 0, 0, 127))
    draw.text((x, y), title, font=font)
    del draw
    return img


# in - string, string, - a url and a title
# saves the url of the image to ~/.wallpaper/url.txt and the title of the image to ~/.wallpaper/title.txt, just
# for reference
def save_info(url, title):
    # Reddit escapes the unicode in json, so when the json is downloaded, the info has to be manually re-encoded
    # and have the unicode characters reprocessed
    # title = title.encode('utf-8').decode('unicode-escape')
    with open(config.walldir + '/url.txt', 'w') as urlinfo:
        urlinfo.write(url)
    with open(config.walldir + '/title.txt', 'w') as titleinfo:
        titleinfo.write(remove_tags(title))


# in - string - title of the picture
# out - string - title without any annoying tags
# removes the [tags] throughout the image
def remove_tags(str):
    return re.sub(' +', ' ', re.sub("[\[\(\<].*?[\]\)\>]", "", str)).strip()
