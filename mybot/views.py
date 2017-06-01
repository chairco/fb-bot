import random
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from mybot.model_cmd import *
from mybot.messenger_api import *
from mybot.fb_setting import *

from quizbot2017.quizzler import users
from quizbot2017.quizzler import questions


def get(im_type, im_id):
    return users.get_user(im_type=im_type,im_id=im_id)


def set(serial, im_type, im_id):
    return users.add_user_im(serial=serial, im_type=im_type, im_id=im_id)


def question_list():
    return questions.get_id_question_pairs()


def post_facebook_message(fbid, recevied_message, reg=False, q=None):
    # user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    # user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': PAGE_ACCESS_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json()
    """
    process: 輸入 game --> 開始玩 --> 輸入 kktix 代號驗證  
    """
    if q is None:
        q = []
    else:
        q = q

    fb = FbMessageApi(fbid)

    if recevied_message == "主畫面":
        data = [
            {
                "type": "postback",
                "title": "猜猜看",
                "payload": "猜猜看"
            },
            {
                "type": "postback",
                "title": "查分數",
                "payload": "查分數"
            }
        ]
        fb.template_message(
            title="選擇",
            image_url="https://pbs.twimg.com/profile_images/851073823357059072/dyff_G3a.jpg",
            subtitle="請選擇",
            data=data)
        return 0

    if recevied_message == "right":
        content = "答對了 ^^ 加油加油！"
        fb.text_message(content)
        return 0

    if recevied_message == "wrong":
        content = "答錯了 QQ 再接再厲！"
        fb.text_message(content)
        return 0

    #if recevied_message == "開始玩":
    #    content = "輸入 kktix 代碼（數字部分）"
    #    fb.text_message(content)
    #    return 0

    #if reg == True and str.isdigit(recevied_message):
    if recevied_message == "開始玩":
        '''
        im_id = fbid
        try:
            users_fb = get(im_type='fb',im_id=im_id)
        except Exception as e:
            users_fb = set(serial=recevied_message, im_type='fb', im_id=im_id)
        content = fbid+', 合法使用者'
        fb.text_message(content)
        '''
        #q = users_fb.get_next_question()
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
        },{
            "type": "web_url",
            "url": "https://facebook.com/Jasons-chatbot-299082580532144/",
            "title": "聯絡作者"
        }
    ]
    fb.template_message(
        title="開始遊戲",
        image_url="https://pbs.twimg.com/profile_images/851073823357059072/dyff_G3a.jpg",
        subtitle="請選擇",
        data=data)


def questions(fbid):
    im_id = fbid
    try:
        users_fb = get(im_type='fb',im_id=im_id)
    except Exception as e:
        users_fb = set(serial=recevied_message, im_type='fb', im_id=im_id)

    q = users_fb.get_next_question()
    return q


class MyBotView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        global answer
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    # pprint(message)
                    print('message')
                    if 'quick_reply' in message['message']:
                        reply = message["message"]["quick_reply"]
                        print(answer)
                        if str(reply['payload']) == answer:
                            post_facebook_message(message['sender']['id'], 'right')
                        else:
                            post_facebook_message(message['sender']['id'], 'wrong')
                    try:
                        post_facebook_message(
                            message['sender']['id'], message['message']['text'], 
                            reg=True
                        )
                    except:
                        return HttpResponse()
                if 'postback' in message:
                    #pprint(message)
                    print('postback')
                    try:
                        question = questions(fbid=message['sender']['id'])
                        answer = question.answer
                        print(answer)
                        post_facebook_message(
                            message['sender']['id'], message['postback']['payload'],
                            q=question
                        )
                    except:
                        return HttpResponse()
        return HttpResponse()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)




