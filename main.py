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


    # alert
    alert = driver.switch_to_alert()
    alert.accept()
    driver.implicitly_wait(10)
    time.sleep(3)


    # 로그인
    input_id = driver.find_element_by_id('username')
    input_pw = driver.find_element_by_id('password')
    input_id.send_keys(email)
    input_pw.send_keys(password)
    input_pw.submit()
    driver.implicitly_wait(10)
    time.sleep(3)


    # alert
    alert = driver.switch_to_alert()
    alert.accept()
    driver.implicitly_wait(10)
    time.sleep(3)


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


    # 로그아웃
    logout_btn = driver.find_element_by_css_selector('#header > div.topmenu > ul > li:nth-child(1) > button')
    logout_btn.click()


    # 브라우저 종료
    driver.quit()


    # 이전 게시물
    with open('prev_posts.json', 'r', encoding='utf-8') as f:
        prev_posts = json.load(f)


    # 새로운 게시물
    new_posts = {}
    for 링크, 정보 in curr_posts.items():
        if 링크 not in prev_posts:
            new_posts[링크] = 정보
            prev_posts[링크] = 정보


    # 파일 쓰기
    with open('prev_posts.json', 'w', encoding='utf-8') as f:
        json.dump(prev_posts, f, indent='\t', ensure_ascii=False)


    headers = {'Content-Type': 'application/json'}
    for 링크, 정보 in new_posts.items():
        content = f'👍제목\n{정보["제목"]}\n👍멘토 {정보["작성자"]}\n👍날짜 {정보["특강일"]}\n👍링크\n{링크}'
        data = {'text':content}
        res = requests.post(slack_url, headers=headers, data=json.dumps(data))
    
    
    if new_posts:
        print(f'[{today.year}-{today.hour}-{today.day}] Notified New Mentoring')
    else:
        print(f'[{today.year}-{today.hour}-{today.day}] No New Metoring')


except:
    headers = {'Content-Type': 'application/json'}
    data = {'text':'❌에러남❌'}
    res = requests.post(slack_url, headers=headers, data=json.dumps(data))
    print(f'[{today.year}-{today.hour}-{today.day}] Error')
