import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
from vk_api import VkUpload
import requests
from gradio_client import Client

session = requests.Session()

vk_session = vk_api.VkApi(token="")

session_api = vk_session.get_api()
client = Client("Gegerout/sirius_summarization")

group_info = session_api.groups.getById()
group_id = group_info[0]['id']

longpool = VkBotLongPoll(vk_session, group_id=group_id)
messages_dict = {}


def send_message(input_id, text):
    vk_session.method("messages.send", {"peer_id": input_id, "message": text, "random_id": time.time()})


for event in longpool.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and (action := event.obj['message'].get('action')):
        if action['type'] == 'chat_invite_user' and action[
            "member_id"] == -group_id:
            upload = VkUpload(vk_session)
            image_url = 'https://image-cdn.essentiallysports.com/wp-content/uploads/peely-fortnite.jpg'
            image = session.get(image_url, stream=True)
            photo = upload.photo_messages(photos=image.raw)[0]
            attachment = 'photo{}_{}'.format(photo['owner_id'], photo['id'])
            session_api.messages.send(
                peer_id=event.message.peer_id,
                random_id=time.time(),
                attachment=attachment,
                message="Добро пожаловать в бота Banana AI. Для полноценной работы бота необходимо дать боту права "
                        "администратора или полный доступ к беседе")
    if event.type == VkBotEventType.MESSAGE_NEW:
        message_time = time.time()
        msg = event.object["message"]["text"].lower()
        peer_id = event.object["message"]["peer_id"]
        if msg == "!сократи":
            if peer_id in messages_dict:
                messages_for_peer = [message_info["message"] for message_info in messages_dict[peer_id]]
                messages_for_peer_str = ".".join(messages_for_peer)
                if len(messages_for_peer_str) < 60:
                    send_message(peer_id, "Чат слишком мал")
                else:
                    send_message(peer_id, "Уже сокращаю)")
                    result = client.predict(
                        text=messages_for_peer_str,
                        api_name="/predict"
                    )
                    send_message(peer_id, result)
                    messages_dict[peer_id] = []
            else:
                send_message(peer_id, "Чат слишком мал")
        else:
            if peer_id not in messages_dict:
                messages_dict[peer_id] = []

            messages_dict[peer_id].append({
                "user_id": event.object["message"]["from_id"],
                "message": event.object["message"]["text"]
            })
