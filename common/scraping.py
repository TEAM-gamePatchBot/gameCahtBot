from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# import urllib.request


def kartScraping():
    options = Options()
    options.binary_location = os.environ.get("GOOGLE_CHROME_PATH")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(
        execution_path=str(os.environ.get("CHROMEDRIVER_PATH")), options=options
    )
    # driver = webdriver.Chrome("/app/.chromedriver/bin/chromedriver", chrome_options=options)
    driver.get("https://kart.nexon.com/Kart/News/Patch/List.aspx?n4pageno=1")

    # 게시판 날짜별 패치 목록
    patchListElements = driver.find_elements_by_xpath('//*[@id="kart_main_sections"]//tbody//a')
    patchList = []

    for i in patchListElements[:1]:
        href = i.get_attribute("href")
        text = i.get_attribute("text")
        patchList.append([text, href])

    # print(patchList)

    for i in patchList:
        link = i[1]  # 세부사항 링크.
        driver.get(link)  # 링크 진입

        stringElement = driver.find_element_by_xpath('//*[@class="board_imgarea"]')
        noticeString = stringElement.text  # 게시글 내용 전부 긁어옴

        subjectElements = driver.find_elements_by_xpath(
            '//*[@class="board_imgarea"]//table'
        )  # 이미지보더에 있는 공지사항
        subjectList = []
        for j in subjectElements:
            subject = j.text
            subjectList.append(subject)

        patch_contents = []
        subject_num = 0
        for line in noticeString.splitlines():
            if subjectList[subject_num] in line:
                patch_contents.append(line.strip())
                if subject_num < len(subjectList) - 1:
                    subject_num += 1
            if "▶" in line:
                patch_contents.append(line.strip())

    driver.quit()
    return patch_contents


kartScraping()
