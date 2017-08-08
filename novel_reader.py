import pyrebase
from bs4 import BeautifulSoup
import urllib.request


def alexa_handler(event, context):
    print(event)
    app_id = ""
    response_size = 10

    response = {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText"
            }
        }
    }

    if event['session']['application']['applicationId'] == app_id:
        request_type = event['request']['type']
        if request_type == 'LaunchRequest':
            response_text = "What would you like to read"
        elif request_type == 'IntentRequest':
            config = {
                "apiKey": "",
                "authDomain": "",
                "databaseURL": "",
                "projectId": "",
                "storageBucket": "",
                "messagingSenderId": ""
            }

            firebase = pyrebase.initialize_app(config)
            auth = firebase.auth()
            user = auth.sign_in_with_email_and_password("", "")
            db = firebase.database()

            intent_name = event['request']['intent']['name']
            if intent_name == 'GetNovels':
                retrieval_size = 100
                for key, val in event['request']['intent']['slots'].items():
                    if key == 'numNovels' and 'value' in val:
                        if val['value'] is not None:
                            retrieval_size = int(val['value'])
                novels = db.child("novels").order_by_key().limit_to_first(retrieval_size).get(user['idToken'])
                response_text = ''
                for novel in novels.each():
                    response_text += novel.key() + ','
            elif intent_name == 'ReadNovel':
                novel_name = ''
                chapter_num = '1'
                for key, val in event['request']['intent']['slots'].items():
                    if key == 'novelName' and 'value' in val:
                        novel_name = val['value']
                    elif key == 'chapterNumber' and 'value' in val:
                        if val['value'] is not None:
                            chapter_num = val['value']
                real_novel_name = \
                    ((db.child("synonyms").order_by_key().equal_to(novel_name).get(user['idToken'])).val())[novel_name]

                response_text = ''
                novel_text = get_novel_text(db, user, real_novel_name, chapter_num)
                if novel_text is not None:
                    text = novel_text.find_all(exclude_paging_links)
                    length = len(text)
                    end = response_size if response_size < length else length

                    for tag in text[0:end]:
                                response_text += tag.string + ' '

                    response['sessionAttributes']['end'] = end
                    response['sessionAttributes']['currentNovel'] = real_novel_name
                    response['sessionAttributes']['currentChapter'] = chapter_num
                else:
                    response_text = "Novel text not found"
            elif intent_name == 'ContinueReading':
                if 'currentNovel' in event['session']['attributes']:
                    if 'currentChapter' in event['session']['attributes']:
                        novel_name = event['session']['attributes']['currentNovel']
                        chapter_num = event['session']['attributes']['currentChapter']

                        novel_text = get_novel_text(db, user, novel_name, chapter_num)
                        if novel_text is not None:
                            text_slice = get_novel_text_slice(novel_text, event, response_size)

                            response_text = text_slice[0]

                            response['sessionAttributes']['end'] = text_slice[1]
                            response['sessionAttributes']['currentNovel'] = novel_name
                            response['sessionAttributes']['currentChapter'] = chapter_num
                        else:
                            response_text = "Novel text not found"
                    else:
                        response_text = 'Nothing to continue reading'
                else:
                    response_text = 'Nothing to continue reading'
            elif intent_name == 'NextChapter':
                if 'currentNovel' in event['session']['attributes']:
                    if 'currentChapter' in event['session']['attributes']:
                        novel_name = event['session']['attributes']['currentNovel']
                        chapter_num = event['session']['attributes']['currentChapter']
                        chapter_num = str((int(chapter_num) + 1))

                        novel_text = get_novel_text(db, user, novel_name, chapter_num)
                        if novel_text is not None:
                            text_slice = get_novel_text_slice(novel_text, event, response_size)

                            response_text = text_slice[0]

                            response['sessionAttributes']['end'] = text_slice[1]
                            response['sessionAttributes']['currentNovel'] = novel_name
                            response['sessionAttributes']['currentChapter'] = chapter_num
                        else:
                            response_text = "Novel text not found"
                    else:
                        response_text = 'Nothing to continue reading'
                else:
                    response_text = 'Nothing to continue reading'
            else:
                response_text = "Intent not recognized"
        elif request_type == 'SessionEndedRequest':
            response_text = "Til next time"
        else:
            response_text = "Failed to recognize request"
    else:
        response_text = "Failed to recognize application"

    response['response']['outputSpeech']['text'] = response_text
    return response


def exclude_paging_links(tag):
    if tag.name == 'p':
        for child in tag.descendants:
            if child.name == 'a':
                return False
        return True
    else:
        return False


def get_novel_text(db, user, title, chapter):
    novel_data = db.child("novels").order_by_key().equal_to(title).get(user['idToken'])
    novel_val = (novel_data.val())[title]
    chapter_url = novel_val['chapter'].replace('{chapterNum}', chapter)
    req = urllib.request.Request(chapter_url, data=None, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, "html.parser")
    return soup.find(itemprop='articleBody')


def get_novel_text_slice(novel_text, event, response_size):
    text = novel_text.find_all(exclude_paging_links)
    length = len(text)
    new_end = -1
    response_text = ''
    if 'end' in event['session']['attributes']:
        end = int(event['session']['attributes']['end'])
        if end < length:
            if response_size + end < length:
                new_end = response_size + end
            else:
                new_end = length

            for tag in text[end:new_end]:
                response_text += tag.string + ' '

            if new_end == length:
                response_text += '. End of chapter. Next chapter?'
        else:
            response_text = "End of chapter. Would you like to read the next chapter?"
    else:
        response_text = 'Missing session data'

    return [response_text, new_end]
