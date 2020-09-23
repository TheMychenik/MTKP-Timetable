import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
import vk_api.exceptions as ex


class VkApi:
    def __init__(self, token: str):
        self.__token = token
        self.session = vk_api.VkApi(token=self.__token)
        self.__vk_api = self.session.get_api()

    def get_api(self):
        return self.__vk_api

    @staticmethod
    def exceptions():
        return ex

    def text_msg(self, peer_id: str, message: str, keyboard=None):
        self.__vk_api.messages.send(user_id=peer_id,
                                    message=message,
                                    keyboard=keyboard,
                                    random_id=get_random_id())

    def photo_msg(self, peer_id: str, path_to_photo, message: str = None):
        # TODO переделать совместно с созданием фоток
        upload = VkUpload(self.__vk_api)
        resp = upload.photo_messages(peer_id=int(peer_id), photos=path_to_photo)
        self.__vk_api.messages.send(user_id=peer_id,
                                    attachment=f"photo{resp[0]['owner_id']}_{resp[0]['id']}_{resp[0]['access_key']}",
                                    message=message,
                                    random_id=get_random_id())

    @property
    def keyboard_main(self):
        keyboard_main = VkKeyboard(one_time=False)
        keyboard_main.add_button('Замены', color=VkKeyboardColor.POSITIVE)
        keyboard_main.add_line()
        keyboard_main.add_button('Сегодня', color=VkKeyboardColor.PRIMARY)
        keyboard_main.add_button('Завтра', color=VkKeyboardColor.PRIMARY)
        keyboard_main.add_line()
        keyboard_main.add_button('Помощь', color=VkKeyboardColor.DEFAULT)
        return keyboard_main.get_keyboard()
