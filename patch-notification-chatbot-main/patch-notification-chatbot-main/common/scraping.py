from selenium import webdriver
import urllib.request

subjectLists = []

def kartScraping():
    driver = webdriver.Chrome("./chromedriver")
    driver.get("https://kart.nexon.com/Kart/News/Patch/List.aspx?n4pageno=1")

    patchListElements = driver.find_elements_by_xpath('//*[@id="kart_main_sections"]//tbody//a')
    patchList = []
    
    
    for i in patchListElements:
        href = i.get_attribute("href")
        text = i.get_attribute("text")
        patchList.append([text, href])

    print(patchList)
    
    for i in patchList:
        link = i[1] # 세부사항 링크.
        driver.get(link) #링크 진입


        stringElement = driver.find_element_by_xpath('//*[@class="board_imgarea"]')
        noticeString = stringElement.text
    ##    print(noticeString)
        patchTime = noticeString.split("일정]\n")[1].split("\n")[0].split("-")[1]
        
    ##    notice=noticeString.split("▶")[1].split('\n기간')[0]
        '''바로 위에 34라인 부분이 소제목 따오는 건데, 텍스트 전체에서 어떻게
    해야될지 모르겠음'''
    
        subjectElements = driver.find_elements_by_xpath('//*[@class="board_imgarea"]//table') #이미지보더에 있는 공지사항
        subjectList = []
        subjectList.append(patchTime)
       
        for j in subjectElements:
            subject = j.text
            subjectList.append(subject)


        subjectLists.append(subjectList)

    for i in subjectLists: #패치 세부 사항
        print(i)
    
    driver.quit()
    return subjectLists

