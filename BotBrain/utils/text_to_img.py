import os

from PIL import Image, ImageDraw, ImageFont

from settings import dirs


def create_photo(user_id, text: str, greencolor: bool):  # color: tuple(R,G,B)
    """
        :param user_id: int or str
        :param text: str
        :param greencolor: bool
            True = зеленый (204, 255, 204)
            False = серый (240, 238, 237)
    """
    color = (204, 255, 204)
    if not greencolor:
        color = (240, 238, 237)
    fontname = os.path.join(dirs['font'], 'OpenSans-Regular.ttf')
    fontsize = 14
    font = ImageFont.truetype(fontname, fontsize)

    preimg = Image.new('RGB', (2000, 1000), color)

    text_draw = ImageDraw.Draw(preimg)
    text_width, text_height = text_draw.multiline_textsize(text, font)
    text_draw.multiline_text((10, 10), text, fill="black", font=font)

    img = preimg.crop((0, 0, text_width + 20, text_height + 24))
    path = os.path.join(dirs['images'], f'{user_id}.png')
    img.save(path, "PNG")
    return path
