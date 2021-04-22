import json, time, requests, datetime
from selenium import webdriver


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
email = config['email']
password = config['password']
chrome_path = config['chrome_path']
board_url = config['board_url']
slack_url = config['slack_url']
today = datetime.datetime.now().now()

print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 시작')
try:
    # 접속
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    options.add_argument("lang=ko_KR")
    driver = webdriver.Chrome(chrome_path, chrome_options=options)
    # driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    # driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
    # driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")
    driver.get(board_url)
    driver.implicitly_wait(10)
    time.sleep(3)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 접속 완료')


    # alert
    alert = driver.switch_to_alert()
    alert.accept()
    driver.implicitly_wait(10)
    time.sleep(3)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] Alert 확인')


    # 로그인
    input_id = driver.find_element_by_id('username')
    input_pw = driver.find_element_by_id('password')
    input_id.send_keys(email)
    input_pw.send_keys(password)
    input_pw.submit()
    driver.implicitly_wait(10)
    time.sleep(3)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 로그인')


    # alert
    alert = driver.switch_to_alert()
    alert.accept()
    driver.implicitly_wait(10)
    time.sleep(3)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] Alert 확인')


    # 현재 게시물
    curr_posts = {}
    table = driver.find_element_by_css_selector('#contentsList > div > div > div > table > tbody')
    rows = table.find_elements_by_tag_name('tr')
    for row in rows:
        a_tag = row.find_element_by_tag_name('a')
        링크 = a_tag.get_attribute('href')
        제목 = a_tag.text
        특강일 = row.find_element_by_css_selector('td:nth-child(4)').text
        작성자 = row.find_element_by_css_selector('td:nth-child(7)').text
        curr_posts[링크] = {
            '제목':제목,
            '작성자':작성자,
            '특강일':특강일,
        }
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 현재 게시물 확인')


    # 로그아웃
    logout_btn = driver.find_element_by_css_selector('#header > div.topmenu > ul > li:nth-child(1) > button')
    logout_btn.click()
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 로그아웃')


    # 브라우저 종료
    driver.quit()
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 브라우저 종료')


    # 이전 게시물
    with open('prev_posts.json', 'r', encoding='utf-8') as f:
        prev_posts = json.load(f)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 이전 게시물 확인')


    # 새로운 게시물
    new_posts = {}
    for 링크, 정보 in curr_posts.items():
        if 링크 not in prev_posts:
            new_posts[링크] = 정보
            prev_posts[링크] = 정보
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 새 게시물 확인')


    # 파일 쓰기
    with open('prev_posts.json', 'w', encoding='utf-8') as f:
        json.dump(prev_posts, f, indent='\t', ensure_ascii=False)
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 이전 게시물 갱신')


    headers = {'Content-Type': 'application/json'}
    for 링크, 정보 in new_posts.items():
        content = f'👍제목\n{정보["제목"]}\n👍멘토 {정보["작성자"]}\n👍날짜 {정보["특강일"]}\n👍링크\n{링크}'
        data = {'text':content}
        res = requests.post(slack_url, headers=headers, data=json.dumps(data))
    
    
    if new_posts:
        print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 알림 발송')
    else:
        print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 새 게시물 없음')


except:
    headers = {'Content-Type': 'application/json'}
    data = {'text':'❌에러남❌'}
    res = requests.post(slack_url, headers=headers, data=json.dumps(data))
    print(f'[{today.year}-{today.month}-{today.day} {today.hour}:{today.minute}] 에러 발생')
