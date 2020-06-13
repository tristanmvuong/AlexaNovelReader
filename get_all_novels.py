import bs4
import urllib.request
import urllib.error


def main():
    base_url = "https://boxnovel.com/novel/page/"
    page_num = 1
    novel_list = ''

    while True:
        req = urllib.request.Request(base_url + str(page_num), data=None, headers={'User-Agent': 'Mozilla/5.0'})

        try:
            page = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if page_num > 1:
                break
            else:
                return
        except urllib.error.URLError as e:
            return
        else:
            soup = bs4.BeautifulSoup(page, 'html.parser')
            for item in soup.find_all('div', class_='post-title'):
                a = item.find('a')
                novel = '"' + a.get_text() + '"' + ',' + \
                        a.get('href').replace('https://boxnovel.com/novel/', '') + ',\n'
                if len(novel) < 200:
                    novel_list += novel

            page_num += 1

    f = open('novels_list.csv', 'w', encoding='utf-8')
    f.write(novel_list)
    f.close()


if __name__ == "__main__":
    main()