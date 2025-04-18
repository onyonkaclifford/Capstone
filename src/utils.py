# import base64
# import io


# def get_image_extension(image_name):
#     return image_name.split(".")[-1]


# def get_resized_image(image, max_width):
#     img_w, img_h = image.size
#     resize_factor = max_width / img_w
#     return (
#         image.resize((max_width, int(img_h * resize_factor)))
#         if img_w > max_width
#         else image
#     )


# def get_base64_encoded_image(image, image_extension):
#     buffer = io.BytesIO()
#     image.save(buffer, "jpeg" if image_extension == "jpg" else image_extension)
#     buffer.seek(0)
#     return base64.b64encode(buffer.read()).decode("UTF-8")


import base64
import collections
import io


def get_image_extension(image_name):
    return image_name.split(".")[-1]


def get_resized_image(image, max_width):
    img_w, img_h = image.size
    resize_factor = max_width / img_w
    return (
        image.resize((max_width, int(img_h * resize_factor)))
        if img_w > max_width
        else image
    )


def get_base64_encoded_image(image, image_extension):
    buffer = io.BytesIO()
    image.save(buffer, "jpeg" if image_extension == "jpg" else image_extension)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("UTF-8")


class RobotToolDict(collections.abc.Mapping):
    def __init__(self, *special_keywords, **kwargs):
        self.__special_keywords = special_keywords
        self._dict = dict(**kwargs)

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        items = self._dict.__getitem__(key)
        params = {}

        for k, v in items:
            if v in self.__special_keywords:
                params[v] = k
            elif v in k:
                params[v] = k[v]

        return params