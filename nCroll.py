import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import time
import requests
from bs4 import BeautifulSoup
import re
import pymysql


# def search_hotdeals(keyword):

#     # 사이트 주소
#     # 120자 넘으면 에러 뜸, 여러 줄로 나눠서 작성
#     url = (
#         "https://www.fmkorea.com/search.php?mid=hotdeal&category=&listStyle=webzine&"
#         "search_keyword={}&search_target=title_content"
#     ).format(keyword)

#     # url에 요청해서 결과물(html)을 r로 받음
#     r = requests.get(url)

#     # r의 내용(html)을 lxml 이란 파서를 써서 BeautifulSoup 을 사용해 분석
#     bs = BeautifulSoup(r.content, "lxml")

#     # bs의 내용 중 li class = li를 가지고 있는 div class = li 요소를 선택
#     # select는 리스트 타입으로 반환
#     divs = bs.select("li.li > div.li")

#     # divs의 결과물 중 필요한 요소를 가져옴
#     for d in divs:
#         # img 클래스 이름이 thumb entered loaded 일때 공백 사이를 .으로 연결해 3가지 요소를 모두 포함한 클래스를 선택한다
#         # 근데 안됨. 그래서 걍 thumb 만 넣음
#         # thumb = 이미지 + @, data-original = 썸넬만
#         images = d.select("img.thumb")[0]
#         image = images.get("data-original")

#         # href = 원글 링크
#         if d.select(".hotdeal_var8"):
#             alink = d.select(".hotdeal_var8")[0]
#         elif d.select(".hotdeal_var8Y"):
#             alink = d.select(".hotdeal_var8Y")[0]
#         else:
#             print("에러: 해당되는 클래스가 없습니다")
#         href = "https://www.fmkorea.com" + alink.get("href")

#         title = re.sub(r'\s+', ' ', alink.text).strip()

#         total = d.select("div.hotdeal_info")[0]
#         infodeal = re.sub(r'\s+', ' ', total.text).strip()

#         # 중복 알림 체크
#         if infodeal not in send_lists:
#             send_info(href, infodeal)
#         else:
#             bot.sendMessage(chat_id, "중복")
#             continue


# def send_info(href, infodeal):
#     bot.sendMessage(chat_id, href)
#     bot.sendMessage(chat_id, infodeal)
#     bot.sendMessage(chat_id, "ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
#     send_lists.append(infodeal)











# 봇에게 특정한 메시지가 도착
def handle_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':
        # '/start' 입력을 받았을 때 메시지 전송
        if msg['text'] == '/start':
            bot.sendMessage(chat_id, '안녕하세요.\n\n사용자가 원하는 핫딜 정보를 제공하는 Fm_bot입니다.' + 
                            '\n\n\n도움이 필요하시면 아래를 클릭해 주세요.' + 
                            '\n\n\n/help    도움말')

        # '/help' 입력을 받았을 때 메시지 전송
        elif msg['text'] == '/help':
            # manual 버튼 생성
            btn_manual = draw_btn('manual')
            bot.sendMessage(chat_id, '어떤 도움이 필요하신가요?', reply_markup=btn_manual)

        # '서치' 입력을 받았을 때 DB에 저장
        elif msg['text'].startswith('/서치'):
            hotdeal_word = msg['text'].replace('/서치', '').strip()
            if hotdeal_word == '':
                bot.sendMessage(chat_id, '키워드를 입력해 주세요.')
            else:
                insert_keyword_db(chat_id, hotdeal_word)

        # '해제' 입력을 받았을 때 DB에 데이터 제거
        elif msg['text'].startswith('/해제'):
            hotdeal_word = msg['text'].replace('/해제', '').strip()
            if hotdeal_word == '':
                bot.sendMessage(chat_id, '키워드를 입력해 주세요.')
            else:
                del_keyword_db(chat_id, hotdeal_word)


# 콜백 함수, GUI 버튼이 눌렸을 때
def on_callback_query(msg): 
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    if query_data == '/manual':
        bot.sendMessage(from_id, '1.  register 버튼을 클릭하여 사용자 정보를 등록해 주세요.' + 
                             "\n\n2.  search 버튼을 클릭하여 관심있는 키워드를 등록해 주세요.")
        # register 버튼 생성
        btn_register = draw_btn('register')
        bot.sendMessage(from_id, '\U00002B07 회원 정보 등록 \U00002B07', reply_markup=btn_register)

        # search 버튼 생성
        btn_search = draw_btn('search')
        bot.sendMessage(from_id, '\U00002B07 제공받으실 알림을 설정해 주세요 \U00002B07', reply_markup=btn_search)

    elif query_data == '/register':
        register_db(from_id)

    elif query_data == '/show_search':
        show_input_keyword(from_id)

    elif query_data == '/show_cmd':
        bot.sendMessage(from_id, '메뉴창을 띄워 드리겠습니다.')
        bot.sendMessage(from_id, '\U00002B07 사용하실 메뉴를 클릭해 주세요 \U00002B07')
        # menu 버튼 생성
        btn_menu = draw_btn('menu')
        bot.sendMessage(from_id, 'keywords: 등록된 키워드 확인\n'+
                                 '/서치(키워드): 키워드 등록\n'+
                                 '/해제(키워드): 키워드 해제', reply_markup=btn_menu)
    
    elif query_data == '/print_keywords':
        print_keywords_db(from_id)


# GUI 버튼 생성
def draw_btn(btn_name):
    if btn_name == 'manual':
        btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='사용법을 알려줘', callback_data='/manual')],
                [InlineKeyboardButton(text='명령어를 보여줘', callback_data='/show_cmd')]
            ])
    
    elif btn_name == 'register':
        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='register', callback_data='/register')],
        ])

    elif btn_name == 'search':
        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='search', callback_data='/show_search')],
        ])

    elif btn_name == 'menu':
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='keywords', callback_data='/print_keywords'),
            InlineKeyboardButton(text='temp', callback_data='/temp')
        ]])

    elif btn_name == 'only_keyword':
        btn = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='keywords', callback_data='/print_keywords'),
        ]])

    return btn


# 사용자에게 키워드 입력 창을 띄워준다
def show_input_keyword(from_id):
    markup = {'force_reply': True}  # 사용자 입력을 강제로 요청 = True
    bot.sendMessage(from_id, '키워드 등록 예시를 알려드리겠습니다.')
    bot.sendMessage(from_id, 'ex) /서치아이폰15, /서치Iphone15', reply_markup=markup)
    bot.sendMessage(from_id, '이후로도 /서치(키워드)를 통해 알람을 설정하실 수 있습니다.')


# db 회원 정보 등록
def register_db(from_id):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()
        insert_keyword = f"INSERT INTO users (user_id) VALUES ({from_id});"
        cur.execute(insert_keyword)
        conn.commit()
        bot.sendMessage(from_id, '회원 정보가 등록되었습니다.')

    except pymysql.IntegrityError as err:
        error_code = err.args[0]
        if error_code == 1062:  # pymysql 에러 코드 1062는 중복 삽입 오류를 나타냅니다.
            bot.sendMessage(from_id, '이미 등록된 사용자입니다')
        else:
            bot.sendMessage(from_id, '에러 발생.')

    finally:
        if 'connection' in locals() and conn.is_connected():
            cur.close()
            conn.close()

# db 키워드 등록
def insert_keyword_db(from_id, hotdeal_word):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()

        # users 테이블에서 user_id가 from_id와 일치하는 user_num 조회
        select_query = f"SELECT user_num FROM users WHERE user_id = '{from_id}'"
        cur.execute(select_query)
        user_row = cur.fetchone()

        if user_row:
            user_num = user_row[0]

            # keywords 테이블에서 동일한 user_num과 word_name을 가진 행이 있는지 확인
            check_query = f"SELECT * FROM keywords WHERE user_num = {user_num} AND word_name = '{hotdeal_word}'"
            cur.execute(check_query)
            existing_row = cur.fetchone()

            if existing_row:
                bot.sendMessage(from_id, f'{hotdeal_word} 키워드는 이미 등록되어 있습니다.')
            else:
                # keywords 테이블에 user_num과 원하는 값을 INSERT
                insert_keyword = f"INSERT INTO keywords (user_num, word_name) VALUES ({user_num}, '{hotdeal_word}')"
                cur.execute(insert_keyword)
                conn.commit()
                bot.sendMessage(from_id, f'{hotdeal_word} 키워드가 등록되었습니다.')
        else:
            bot.sendMessage(from_id, '사용자를 찾을 수 없습니다.')
            bot.sendMessage(from_id, '회원 정보를 등록해 주십시오.')

            # 편의성 좋게 register 버튼 생성
            btn_register = draw_btn('register')
            bot.sendMessage(from_id, '\U00002B07 회원 정보 등록 \U00002B07', reply_markup=btn_register)

    # user_num과 word_name이 모두 같은 경우에만 예외처리
    except pymysql.IntegrityError as err:
        error_code = err.args[0]
        if error_code == 1062:
            bot.sendMessage(from_id, '이미 등록된 키워드입니다.')
        else:
            bot.sendMessage(from_id, '에러 발생.')

    finally:
        if 'connection' in locals() and conn.is_connected():
            cur.close()
            conn.close()


# db에 등록된 사용자 키워드 리스트 출력
def print_keywords_db(from_id):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()

        # user_id로 user_num을 찾기
        find_user_query = f"SELECT user_num FROM users WHERE user_id = '{from_id}'"
        cur.execute(find_user_query)
        user_result = cur.fetchone()

        if user_result:
            user_num = user_result[0]

            # user_num을 기준으로 word_name 선택
            select_word_query = f"SELECT word_name FROM keywords WHERE user_num = {user_num}"
            cur.execute(select_word_query)
            word_names = cur.fetchall()

            if word_names:
                bot.sendMessage(from_id, '\U00002B07 등록된 키워드를 알려드리겠습니다 \U00002B07')
                for i in word_names:
                    word = str(i)
                    bot.sendMessage(from_id, word[2:-3])

            else:
                bot.sendMessage(from_id, '등록된 키워드가 없습니다.')
                bot.sendMessage(from_id, '키워드를 등록해 주십시오.')
                bot.sendMessage(from_id, '/서치(키워드)')

        else:
            bot.sendMessage(from_id, '사용자를 찾을 수 없습니다.')
            bot.sendMessage(from_id, '회원 정보를 등록해 주십시오.')

            # 편의성 좋게 register 버튼 생성
            btn_register = draw_btn('register')
            bot.sendMessage(from_id, '\U00002B07 회원 정보 등록 \U00002B07', reply_markup=btn_register)
    
    except pymysql.Error as e:
        bot.sendMessage(from_id, f'에러 발생\n{e}')

    finally:
        if 'conn' in locals() and conn.open:
            cur.close()
            conn.close()


# db 키워드 삭제
def del_keyword_db(from_id, hotdeal_word):
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()

        # user_id로 user_num을 찾기
        find_user_query = f"SELECT user_num FROM users WHERE user_id = '{from_id}'"
        cur.execute(find_user_query)
        user_result = cur.fetchone()

        # 키워드 제거
        if user_result:
            user_num = user_result[0]

            # 키워드 존재 여부 확인
            check_keyword_query = f"SELECT word_name FROM keywords WHERE user_num = {user_num} AND word_name = '{hotdeal_word}'"
            cur.execute(check_keyword_query)
            keyword_exists = cur.fetchone()

            if keyword_exists:
                del_keyword = f"DELETE FROM keywords WHERE user_num = {user_num} AND word_name = '{hotdeal_word}'"
                cur.execute(del_keyword)
                conn.commit()
                bot.sendMessage(from_id, f'{hotdeal_word} 키워드가 삭제되었습니다.')
            else:
                bot.sendMessage(from_id, f'등록된 키워드가 아닙니다.')
                bot.sendMessage(from_id, '정확한 키워드명을 확인해 주십시오.')
                btn_only_keyword = draw_btn('only_keyword')
                bot.sendMessage(from_id, '\U00002B07 등록된 키워드 확인 \U00002B07', reply_markup=btn_only_keyword)

        else:
            bot.sendMessage(from_id, '등록된 사용자가 아닙니다.')
            bot.sendMessage(from_id, '회원 등록을 먼저 진행해 주십시오.')

            # 편의성 좋게 register 버튼 생성
            btn_register = draw_btn('register')
            bot.sendMessage(from_id, '\U00002B07 회원 정보 등록 \U00002B07', reply_markup=btn_register)

    except pymysql.Error as e:
        bot.sendMessage(from_id, f'에러 발생\n{e}')

    finally:
        if 'conn' in locals() and conn.open:
            cur.close()
            conn.close()




def search_hotdeals(keyword):

    # 핫딜 정보 담김
    href_arr = []
    infodeal_arr = []
    title_arr = []
    regdate_arr = []
    author_arr = []

    # 사이트 주소
    # 120자 넘으면 에러 뜸, 여러 줄로 나눠서 작성
    url = (
        "https://www.fmkorea.com/search.php?mid=hotdeal&category=&listStyle=webzine&"
        "search_keyword={}&search_target=title"
    ).format(keyword)

    # url에 요청해서 결과물(html)을 r로 받음
    r = requests.get(url)

    # r의 내용(html)을 lxml 이란 파서를 써서 BeautifulSoup 을 사용해 분석
    bs = BeautifulSoup(r.content, "lxml")

    # bs의 내용 중 li class = li를 가지고 있는 div class = li 요소를 선택
    # select는 리스트 타입으로 반환
    divs = bs.select("li.li > div.li")

    cnt = 0

    # divs의 결과물 중 필요한 요소를 가져옴
    for d in divs:
        if cnt == 3:
            break
        
        # img 클래스 이름이 thumb entered loaded 일때 공백 사이를 .으로 연결해 3가지 요소를 모두 포함한 클래스를 선택한다
        # 근데 안됨. 그래서 걍 thumb 만 넣음
        # thumb = 이미지 + @, data-original = 썸넬만
        # images = d.select("img.thumb")[0]
        # image = images.get("data-original")

        # 펨코 핫딜에서 이미 지나간 핫딜은 글자 중앙에 취소선(-)이 달려 있음
        # 이런 경우 var8이 아닌 var8Y 클래스를 가지고 있으니 조건문을 사용해 에러 방지
        # href = 원글 링크
        if d.select(".hotdeal_var8"):
            alink = d.select(".hotdeal_var8")[0]
        elif d.select(".hotdeal_var8Y"):
            alink = d.select(".hotdeal_var8Y")[0]
        else:
            print("에러: 해당되는 클래스가 없습니다")

        href = "https://www.fmkorea.com" + alink.get("href")
        href_arr.append(href)

        # 핫딜의 정보를 가지고 있는 div 클래스 hotdeal_info를 가져옴
        # 쇼핑몰 / 가격 / 배송비를 가지고 있음
        infodeal = d.select("div.hotdeal_info")[0]
        infodeal = re.sub(r'\s+', ' ', infodeal.text).strip()
        infodeal_arr.append(infodeal)

        # 핫딜 계시글 제목 정보
        # re 모듈
        # 정규 표현식을 사용하여 연속된 공백을 1개로 치환하고 양쪽 공백을 제거
        # r: \(역슬래쉬)를 이스케이프 문자로 처리하지 않음. \n같은 줄바꿈에서 사용되는 \가 아닌 정규 표현식 용 \으로 사용을 하겠다~
        # \s: 공백 문자를 나타내는 이스케이프 시퀀스
        # +: 1회 이상 반복을 나타내는 메타 문자
        # alink에서 text를 뽑아 가공
        # <a> 태그 사이의 내용 = .text
        title = re.sub(r'\s+', ' ', alink.text).strip()
        title = title[0:-5]
        title_arr.append(title)

        # 핫딜 계시글이 써진 날짜 정보
        regdate = d.select("div > span.regdate")[0]
        regdate = re.sub(r'\s+', ' ', regdate.text).strip()
        regdate_arr.append(regdate)

        # 핫딜 계시글을 작성한 유저 정보
        author = d.select("div > span.author")[0]
        author = re.sub(r'\s+', ' ', author.text).strip()
        author = author[2:]
        author_arr.append(author)
        cnt += 1

    hotdeal_check = hotdeal_duplicate_check(title_arr, regdate_arr, author_arr, href_arr, infodeal_arr)
    
    return hotdeal_check





# 핫딜 중복 검사 + db 저장
def hotdeal_duplicate_check(titles, regdates, authors, hrefs, infodeals):
    
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()
        check_complete_titles = []
        check_complete_infodeals = []
        check_complete_hrefs = []

        # 계시글 제목, 날짜, 작성자가 모두 같다면
        for title, regdate, author, href, infodeal in zip(titles, regdates, authors, hrefs, infodeals):
            sql = f"SELECT * FROM croll_words WHERE deal_title = '{title}' AND deal_regdate = '{regdate}' AND deal_author = '{author}'"
            cur.execute(sql)
            result = cur.fetchone()

            if result:
                continue
            else:
                check_complete_titles.append(title)
                check_complete_infodeals.append(infodeal)
                check_complete_hrefs.append(href)
                insert_keyword = f"INSERT INTO croll_words (deal_title, deal_regdate, deal_author) VALUES ('{title}', '{regdate}', '{author}')"
                cur.execute(insert_keyword)
                conn.commit()
            

        check_hotdeals = [check_complete_titles, check_complete_infodeals, check_complete_hrefs]

        return check_hotdeals

    except pymysql.Error as e:
        print(f"Error: {e}")

    finally:
        if 'conn' in locals() and conn.open:
            cur.close()
            conn.close()





def croll():
    try:
        conn = pymysql.connect(host='127.0.0.1', user='root', password='pybotpass123@', db='craw', charset='utf8')
        cur = conn.cursor()

        # 중복 제거 등록된 모든 키워드 & 각 키워드를 등록한 user_num
        query = "SELECT word_name, GROUP_CONCAT(user_num) AS user_nums FROM keywords GROUP BY word_name;"
        cur.execute(query)
        results = cur.fetchall()

        # 크롤링 + 중복체크 + db 저장 + 핫딜 전송
        for row in results:
            word_name = row[0]
            user_nums = row[1].split(',')  # 쉼표로 구분된 user_num을 리스트로 분할
            send_hotdeals = search_hotdeals(word_name) # 크롤링 + 중복체크 + db 저장 후 전송할 데이터 반환
            
            for user_num in user_nums: # 핫딜 전송
                find_chat_id = f"select user_id from users where user_num = {user_num}"
                cur.execute(find_chat_id)
                chat_id = cur.fetchone()
                chat_id = chat_id[0]
                for title, infodeal, href in zip(send_hotdeals[0], send_hotdeals[1], send_hotdeals[2]):
                    bot.sendMessage(chat_id, f'\U00002B07 {title} \U00002B07')
                    bot.sendMessage(chat_id, infodeal)
                    bot.sendMessage(chat_id, href)
        
    except pymysql.Error as e:
        print(f"Error: {e}")

    finally:
        if 'conn' in locals() and conn.open:
            cur.close()
            conn.close()






# 텔레그램 봇 토큰 설정
bot = telepot.Bot('6450289450:AAEZZXbQBJmFKIW7R_BOGubo5lEXs3qoFM0')

# 메시지 핸들러 등록
bot.message_loop({'chat': handle_message, 'callback_query': on_callback_query})

# 봇이 계속해서 메시지를 받을 수 있도록 대기
while True:
    croll()
    time.sleep(10) # 딜레이

