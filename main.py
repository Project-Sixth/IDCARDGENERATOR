from PIL import Image as PILI
from PIL import ImageFont as PILF
from PIL import ImageDraw as PILD
import argparse
import yaml
import os

parser = argparse.ArgumentParser()
parser.add_argument("files", type=str, nargs='+')
args = parser.parse_args()

def main(filepath):
    carddict = yaml.safe_load(open(f'{filepath}', 'r', encoding='utf-8'))
    builderdict = yaml.safe_load(open(f'configs/{carddict["config"]}.yaml', 'r', encoding='utf-8'))

    # Make dictionary with loaded items
    loaded_images = {}
    def loadImage(path):
        if path not in loaded_images:
            loaded_images[path] = PILI.open(open(f'resources/{path}', 'rb'))
        return loaded_images[path]
    loaded_fonts = {}
    def loadFont(path, size):
        if (path, size) not in loaded_fonts:
            loaded_fonts[(path, size)] = PILF.truetype(f'resources/{path}', size)
        return loaded_fonts[(path, size)]

    def transposeImage(img, transpositionIterable):
        if not transpositionIterable:
            return img
        
        timg = img
        for i in transpositionIterable:
            if i == 'cw':
                timg = timg.transpose(2)
            elif i == 'ccw':
                timg = timg.transpose(4)
            elif i == 'fliph':
                timg = timg.transpose(1)
            elif i == 'flipv':
                timg = timg.transpose(0)
            elif i == '180':
                timg = timg.transpose(3)
            else:
                raise Exception(f"Wrong transposition type {i}. Can only be cw, ccw, fliph, flipv, 180 in the list.")
        return timg

    def getFromDictionary(img_build_step, id, default=None):
        if img_build_step in carddict['substitutes']:
            # If we have dict instead of string, then try to return part of dict.
            if type(carddict['substitutes'][image_building_step]) == dict:
                if id in carddict['substitutes'][image_building_step]:
                    return carddict['substitutes'][image_building_step][id]
                elif id in builderdict[img_build_step]:
                    return builderdict[img_build_step][id]
                else:
                    return default
            elif type(carddict['substitutes'][image_building_step]) == str:
                if builderdict[image_building_step]["type"] == 'image':
                    if id == 'path':
                        return carddict['substitutes'][image_building_step]
                    elif id in builderdict[img_build_step]:
                        return builderdict[img_build_step][id]
                    else:
                        return default
                elif builderdict[image_building_step]["type"] == 'text':
                    if id == 'text':
                        return carddict['substitutes'][image_building_step]
                    elif id in builderdict[img_build_step]:
                        return builderdict[img_build_step][id]
                    else:
                        return default
                elif builderdict[image_building_step]["type"] == 'transposedtext':
                    if id == 'text':
                        return carddict['substitutes'][image_building_step]
                    elif id in builderdict[img_build_step]:
                        return builderdict[img_build_step][id]
                    else:
                        return default
                else:
                    raise Exception(f"Tried to get {builderdict[image_building_step]['type']} for {id}, but I don't know how to deal with strings there!")
            else:
                raise Exception(f"Not dictionary or string in substitutes! Error @ {img_build_step}")
        elif id in builderdict[img_build_step]:
            return builderdict[img_build_step][id]
        else:
            return default


    # Start compiling image
    img = PILI.new('RGBA', builderdict['size'])
    imgdraw = PILD.Draw(img)

    # Determine order of imagebuilding
    image_building_order = builderdict["order"] if "order" in builderdict else [x for x in builderdict.keys() if x not in ['size']]

    # Start building
    for image_building_step in image_building_order:
        if builderdict[image_building_step]["type"] == 'image':
            ipath = getFromDictionary(image_building_step, 'path')
            tmp = transposeImage(loadImage(ipath), getFromDictionary(image_building_step, 'transposition', tuple()))
            img.paste(tmp, getFromDictionary(image_building_step, 'position', (0,0)), mask=tmp.convert('RGBA'))
        elif builderdict[image_building_step]["type"] == 'text':
            fpath = getFromDictionary(image_building_step, 'font', None)
            fsize = getFromDictionary(image_building_step, 'size', 10)
            tmp = loadFont(fpath, fsize)
            imgdraw.text(xy=getFromDictionary(image_building_step, 'position', (0,0)), \
                text=getFromDictionary(image_building_step, 'text', ''), \
                font=tmp, \
                align=getFromDictionary(image_building_step, 'align', 'left'), \
                anchor=getFromDictionary(image_building_step, 'anchor', 'la'), \
                fill=getFromDictionary(image_building_step, 'color', '#ffffff'))
        elif builderdict[image_building_step]["type"] == 'transposedtext':
            fpath = getFromDictionary(image_building_step, 'font', None)
            fsize = getFromDictionary(image_building_step, 'size', 10)
            tmp = loadFont(fpath, fsize)
            tmpsize = tmp.getbbox(getFromDictionary(image_building_step, 'text', ''))
            tmpi = PILI.new("RGBA", (tmpsize[2], tmpsize[3]))
            tmpid = PILD.Draw(tmpi)
            tmpid.text(xy=(0,0), \
                text=getFromDictionary(image_building_step, 'text'), \
                font=tmp, \
                fill=getFromDictionary(image_building_step, 'color', '#ffffff'))
            ttmpi = transposeImage(tmpi, getFromDictionary(image_building_step, 'transposition', tuple()))
            img.paste(ttmpi, getFromDictionary(image_building_step, 'position', (0,0)), mask=ttmpi)

    img.save(f'{filepath}.png', format='PNG')

if __name__ == "__main__":
    for fd in args.files:
        if os.path.isfile(fd):
            try:
                main(fd)
            except:
                print(f'{fd} is not possible to parse, so we did not.')
        elif os.path.isdir(fd):
            for fdd in os.listdir(fd):
                if fdd.endswith('.yaml') or fdd.endswith('.yml'):
                    try:
                        main(f'{fd}/{fdd}')
                    except:
                        print(f'{fd}/{fdd} is not possible to parse, so we did not.')