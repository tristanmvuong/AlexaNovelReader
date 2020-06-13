from bs4 import BeautifulSoup
import urllib.request


host = 'https://boxnovel.com/novel/'


def alexa_handler(event, context):
    app_id = "amzn1.ask.skill.00881ef7-313d-4e33-b116-aeadb33598fc"
    response_size = 20

    response = {
        "version": "1.0",
        "sessionAttributes": {},
        "response": {
            "outputSpeech": {
                "type": "PlainText"
            },
            "shouldEndSession": "false"
        }
    }

    if event['session']['application']['applicationId'] == app_id:
        request_type = event['request']['type']
        if request_type == 'LaunchRequest':
            response_text = "What would you like to read"
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']

            if intent_name == 'ReadNovel':
                slots_key = event['request']['intent']['slots']

                if slots_key['novelName']['resolutions']['resolutionsPerAuthority'][0]['status']['code'] == \
                        'ER_SUCCESS_NO_MATCH':
                    response_text = "Failed to recognize request"
                else:
                    novel_name = \
                        slots_key['novelName']['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

                    if 'value' in slots_key['chapterNumber']:
                        chapter_num = slots_key['chapterNumber']['value']
                    else:
                        chapter_num = '1'

                    novel_text = get_novel_text(novel_name, chapter_num)
                    if novel_text is not None:
                        text_slice = get_novel_text_slice(novel_text, 0, response_size)

                        response_text = text_slice[0]

                        response['sessionAttributes']['end'] = text_slice[1]
                        response['sessionAttributes']['currentNovel'] = novel_name
                        response['sessionAttributes']['currentChapter'] = chapter_num
                    else:
                        response_text = "Novel text not found"
            elif intent_name == 'ContinueReading':
                if 'attributes' not in event['session']:
                    response_text = "Nothing to continue reading"
                elif 'currentNovel' in event['session']['attributes']:
                    if 'currentChapter' in event['session']['attributes']:
                        novel_name = event['session']['attributes']['currentNovel']
                        chapter_num = event['session']['attributes']['currentChapter']

                        novel_text = get_novel_text(novel_name, chapter_num)
                        if novel_text is not None:
                            if 'end' in event['session']['attributes']:
                                end = int(event['session']['attributes']['end'])

                                text_slice = get_novel_text_slice(novel_text, end, response_size)

                                response_text = text_slice[0]

                                response['sessionAttributes']['end'] = text_slice[1]
                                response['sessionAttributes']['currentNovel'] = novel_name
                                response['sessionAttributes']['currentChapter'] = chapter_num
                            else:
                                response_text = 'Missing session data'
                        else:
                            response_text = "Novel text not found"
                    else:
                        response_text = 'Nothing to continue reading'
                else:
                    response_text = 'Nothing to continue reading'
            elif intent_name == 'NextChapter':
                if 'attributes' not in event['session']:
                    response_text = "Nothing to continue reading"
                elif 'currentNovel' in event['session']['attributes']:
                    if 'currentChapter' in event['session']['attributes']:
                        novel_name = event['session']['attributes']['currentNovel']
                        chapter_num = event['session']['attributes']['currentChapter']
                        chapter_num = str((int(chapter_num) + 1))

                        novel_text = get_novel_text(novel_name, chapter_num)
                        if novel_text is not None:
                            text_slice = get_novel_text_slice(novel_text, 0, response_size)

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


def get_novel_text(title, chapter_num):
    chapter_url = host + title + 'chapter-' + str(chapter_num)
    req = urllib.request.Request(chapter_url, data=None, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page, "html.parser")
    return soup.find('div', class_='reading-content')


def get_novel_text_slice(novel_text, start, response_size):
    text = novel_text.find_all('p')
    length = len(text)
    new_end = -1
    response_text = ''
    if start < length:
        if response_size + start < length:
            new_end = response_size + start
        else:
            new_end = length

        for tag in text[start:new_end]:
            response_text += tag.get_text() + ' '

        if new_end == length:
            response_text += '. End of chapter. Next chapter?'
    else:
        response_text = "End of chapter. Would you like to read the next chapter?"

    return [response_text, new_end]
