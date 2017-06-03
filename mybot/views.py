import random
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from mybot.messenger_api import *
from mybot.fb_setting import *

from quizbot2017.quizzler import users, questions, im


def get(im_type, im_id):
    return users.get_user(im_type=im_type,im_id=im_id)


def set(ticket, serial, im_type, im_id):
    return users.add_user_im(ticket=ticket, serial=serial, im_type=im_type, im_id=im_id)


def question_list():
    return questions.get_id_question_pairs()


def questions(fbid):
    im_id = fbid
    try:
        users_fb = get(im_type='fb', im_id=im_id)
    except Exception as e:
        #TODO hotcode assign serial = 1, QQ
        raise e

    q = users_fb.get_next_question()
    return q


def post_facebook_message(fbid, recevied_message, q=None):
    # user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    # user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json()
    """Process:
    查詢 id -> 第一次進入遊戲 -> 詢問 mail, serial -> 綁定 fb or line id -> 開始遊戲
           -> 第二次進入遊戲 -> 開始遊戲
    """
    if q is None:
        q = []
    else:
        q = q

    fb = FbMessageApi(fbid)

    if recevied_message == "not_exist_"+str(fbid):
        data = [
        {
            "type": "postback",
            "title": "輸入信箱開始註冊",
            "payload": "register_user"
        },
        {
            "type": "postback",
            "title": "不玩了",
            "payload": "exit"
        }
        ]
        fb.template_message(
            title="開始註冊",
            image_url="https://pbs.twimg.com/profile_images/851073823357059072/dyff_G3a.jpg",
            subtitle="歡迎 PyConTW 2017 大會遊戲",
            data=data)
        return 0

    if recevied_message == "right"+str(fbid):
        content = "答對了 ^^ 加油加油！"
        fb.text_message(content)
        return 0

    if recevied_message == "wrong"+str(fbid):
        content = "答錯了 QQ 再接再厲！"
        fb.text_message(content)
        return 0

    if recevied_message == "查分數":
        content = "你目前的分數：{}".format(
            get(im_type='fb', im_id=str(fbid)).get_current_score()
        )
        fb.text_message(content)
        return 0

    if recevied_message == "exit":
        fb.text_message("記得要再回來啊～～～～！")
        return 0

    if recevied_message == "register_user":
        im.activate_registration_session(im_type='fb', im_id=str(fbid))
        fb.text_message("請輸入註冊在 kktix 電子序號(ex:1)")
        return 0

    if im.is_registration_session_active(im_type='fb',im_id=fbid):
        if str.isdigit(recevied_message):
            try:
                users_fb = get(im_type='fb', im_id=str(fbid))
                im.complete_registration_session(im_type='fb', im_id=str(fbid))
                fb.text_message('已經註冊了')
            except Exception as e:
                users_fb = set(
                    ticket='speaker',
                    serial=str(recevied_message), 
                    im_type='fb', im_id=str(fbid)
                )
                print(users_fb)
                fb.text_message('註冊成功可以開始玩囉！')
                im.complete_registration_session(im_type='fb', im_id=str(fbid))
                raise e
        else:
            fb.text_message('不合法的 kktix 序號，請再次輸入')
        return 0

    if recevied_message == "clean":
        fb.text_message('清除狀態，雄壯威武！')
        im.complete_registration_session(im_type='fb', im_id=str(fbid))
        return 0

    if recevied_message == "開始玩":
        r = random.randint(0, 3)
        q.wrong_choices.insert(r, q.answer)

        data = [
            {
                "content_type": "text",
                "title": q.wrong_choices[0],
                "payload": q.wrong_choices[0]
            },
            {
                "content_type": "text",
                "title": q.wrong_choices[1],
                "payload": q.wrong_choices[1]
            },
            {
                "content_type": "text",
                "title": q.wrong_choices[2],
                "payload": q.wrong_choices[2]
            },
            {
                "content_type": "text",
                "title": q.wrong_choices[3],
                "payload": q.wrong_choices[3]
            }
        ]
        fb.quick_reply_message(
            text=q.message,
            quick_replies=data)
        return 0
    
    data = [
        {
            "type": "postback",
            "title": "開始玩",
            "payload": "開始玩"
        },
        {
            "type": "postback",
            "title": "不玩了",
            "payload": "exit"
        }
    ]
    fb.template_message(
        title="開始遊戲",
        image_url="https://pbs.twimg.com/profile_images/851073823357059072/dyff_G3a.jpg",
        subtitle="請選擇",
        data=data)


class MyBotView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    # pprint(message)
                    print('message')
                    if 'quick_reply' in message['message']:
                        reply = message["message"]["quick_reply"]
                        get_current = im.get_current_question(
                            im_type='fb', im_id=str(message['sender']['id'])
                        )
                        print(get_current.answer)
                        if str(reply['payload']) == str(get_current.answer):
                            # 設定分數
                            get(im_type='fb', im_id=str(message['sender']['id'])).save_answer(question=get_current, correctness=True)
                            post_facebook_message(
                                message['sender']['id'], 
                                'right'+str(message['sender']['id'])
                            )
                        else:
                            # 設定分數
                            get(im_type='fb', im_id=str(message['sender']['id'])).save_answer(question=get_current, correctness=False)
                            post_facebook_message(message['sender']['id'], 
                                'wrong'+str(message['sender']['id'])
                            )
                    try:
                        post_facebook_message(
                            message['sender']['id'], message['message']['text']
                        )
                    except:
                        return HttpResponse()

                if 'postback' in message:
                    #pprint(message)
                    print('postback')
                    if message['postback']['payload'] == 'register_user':
                        print('register_user')
                        post_facebook_message(
                            message['sender']['id'], 'register_user'
                        )
                    elif message['postback']['payload'] == 'exit':
                        print('exit')
                        post_facebook_message(
                            message['sender']['id'], 'exit'
                        )
                    else:
                        try:
                            question = questions(fbid=message['sender']['id'])
                            print(question.answer)
                            im.set_current_question(
                                question=question, im_type='fb', im_id=str(message['sender']['id'])
                            )
                            post_facebook_message(
                                message['sender']['id'], message['postback']['payload'],
                                q=question
                            )
                        except:
                            post_facebook_message(
                                message['sender']['id'], "not_exist_"+str(message['sender']['id'])
                            )
        return HttpResponse()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)




