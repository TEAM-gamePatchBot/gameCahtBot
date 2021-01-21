from selenium import webdriver

# import urllib.request


def kartScraping():
    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://kart.nexon.com/Kart/News/Patch/List.aspx?n4pageno=1")

    patchListElements = driver.find_elements_by_xpath('//*[@id="kart_main_sections"]//tbody//a')
    patchList = []

    for i in patchListElements[:1]:
        href = i.get_attribute("href")
        text = i.get_attribute("text")
        patchList.append([text, href])

    print(patchList)

    for i in patchList:
        link = i[1]  # 세부사항 링크.
        driver.get(link)  # 링크 진입

        stringElement = driver.find_element_by_xpath('//*[@class="board_imgarea"]')
        noticeString = stringElement.text

        subjectElements = driver.find_elements_by_xpath(
            '//*[@class="board_imgarea"]//table'
        )  # 이미지보더에 있는 공지사항
        subjectList = []
        for j in subjectElements:
            subject = j.text
            subjectList.append(subject)
        print(subjectList)

        with open("latest.txt", "w") as f:
            f.write(noticeString)

        patch_contents = []
        with open("./latest.txt", "r") as f:
            lines = f.readlines()
            subject_num = 0
            for line in lines:
                if subjectList[subject_num] in line:
                    patch_contents.append(line.strip())
                    if subject_num < len(subjectList) - 1:
                        subject_num += 1
                if "▶" in line:
                    patch_contents.append(line.strip())

    driver.quit()
    for i in patch_contents:
        print(i)


kartScraping()
