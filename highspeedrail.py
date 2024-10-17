# -*- coding: utf-8 -*-
"""
高鐵訂票
"""
# from flask import Flask,request,render_template
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import requests
from time import sleep
import ddddocr
# import os
# from datetime import datetime
# import mariadb

def _hsrsearch(transit_detail, hsr_search_ticket, user_info):
    # 參數
    departure_stop = transit_detail["departure_stop"] # 起始站，須給
    arrival_stop = transit_detail["arrival_stop"]       # 到達站，須給
    departure_time_year = int(transit_detail["departure_time_year"])
    departure_time_month = int(transit_detail["departure_time_month"])
    departure_time_day = int(transit_detail["departure_time_day"])
    transit_number = transit_detail["transit_number"] #班次，須給
    # 爬蟲
    chrome_options = Options()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])# 隱藏自動化標籤
    if user_info["headless"] == "T":
        chrome_options.add_argument("--headless") # 無頭模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')# 禁用自動化標籤
    # chrome_options.binary_location = '/app/.apt/usr/bin/google-chrome'  # Chrome location in Heroku
    
    myhead={"user-agent":"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    'Accept': 'application/json'}
    chrome_options.add_argument("user-agent={}".format(myhead["user-agent"]))
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Chrome(executable_path='/app/.chromedriver/bin/chromedriver', options=chrome_options)
    driver.get("https://irs.thsrc.com.tw/IMINT/")
    driver.find_element(By.CSS_SELECTOR,'button.policy-btn-accept').click()   # 安全cookie"同意"
    # 輸入預訂車票基本資料
    driver.find_elements(By.NAME,"bookingMethod")[1].click()   # 車次查詢
    Select(driver.find_element(By.NAME, "selectStartStation")).select_by_visible_text(departure_stop)  # 出發站    
    Select(driver.find_element(By.NAME, "selectDestinationStation")).select_by_visible_text(arrival_stop)  # 抵達站
    try:
        driver.find_elements(By.CSS_SELECTOR,'div.form-group')[2].click()#點日曆
        month_map = {1: "一月", 2: "二月", 3: "三月", 4: "四月",5: "五月", 6: "六月", 7: "七月", 8: "八月",9: "九月", 10: "十月", 11: "十一月", 12: "十二月"}
        month_name = month_map[int(departure_time_month)]
        departure_time = driver.find_element(By.CSS_SELECTOR, f'div.dayContainer span.flatpickr-day[aria-label="{month_name} {departure_time_day}, {departure_time_year}"]')
        driver.execute_script("arguments[0].click();", departure_time)
    except:
        ans="輸入日期有誤"
        driver.quit()
        return ans
    driver.find_element(By.NAME,"toTrainIDInputField").send_keys(transit_number)
    Select(driver.find_element(By.NAME, "ticketPanel:rows:0:ticketAmount")).select_by_visible_text(hsr_search_ticket["ft"])   # 全票
    Select(driver.find_element(By.NAME, "ticketPanel:rows:1:ticketAmount")).select_by_visible_text(hsr_search_ticket["ct"])   # 孩童票
    Select(driver.find_element(By.NAME, "ticketPanel:rows:2:ticketAmount")).select_by_visible_text(hsr_search_ticket["lt"])   # 愛心票
    Select(driver.find_element(By.NAME, "ticketPanel:rows:3:ticketAmount")).select_by_visible_text(hsr_search_ticket["ot"])   # 敬老票
    Select(driver.find_element(By.NAME, "ticketPanel:rows:4:ticketAmount")).select_by_visible_text(hsr_search_ticket["colt"]) # 大學生票
    
    check_ticket = 0
    for ii in hsr_search_ticket.values():
        check_ticket += int(ii)
    
    if departure_stop == arrival_stop:
        ans = "出發站與抵達站，不可同站"
        driver.quit()
        return ans
    elif check_ticket == 0:
        ans = "購票張數不可為零"
        driver.quit()
        return ans
    print("sucess")
    #----------------------------
    
    #獲取驗證圖片、辨識、發送驗證碼
    while True:
        try:
            r=driver.page_source
            soup=BeautifulSoup(r, "html.parser")
            image=soup.select_one("#BookingS1Form_homeCaptcha_passCode")
            image_url="https://irs.thsrc.com.tw" + image.get("src") 
            myhead={"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                    'Accept': 'application/json'} #須送'Accept': 'application/json'
            session = requests.Session()
            r_image=session.get(image_url,headers=myhead,timeout=15) 
            with open ("write.jpg",'wb') as file: #下載驗證圖片
                for b in r_image:
                    file.write(b)
            ocr = ddddocr.DdddOcr()
            with open('write.jpg', 'rb') as f:  # 開啟圖片提供ddddocr讀取
                img_bytes = f.read()
            ans = ocr.classification(img_bytes)
            if len(ans)!=4:
                driver.find_element(By.ID,'BookingS1Form_homeCaptcha_reCodeLink').click()
                continue
            driver.find_element(By.ID,"securityCode").send_keys(ans)
            driver.find_element(By.NAME,'SubmitButton').click() #發送
            r3 = driver.page_source
            sleep(2)
            if "檢測碼輸入錯誤，請確認後重新輸入，謝謝！" in r3:
                driver.find_elements(By.NAME,"bookingMethod")[1].click()#車次查詢
                driver.find_element(By.NAME,"toTrainIDInputField").clear()
                driver.find_element(By.NAME,"toTrainIDInputField").send_keys(transit_number)
                continue
            elif "請輸入去程車次號碼" in r3:
                ans = "車次號碼有誤"
                driver.quit()
                return ans
            elif "去程查無可售車次或選購的車票已售完，請重新輸入訂票條件。" in r3:
                ans = "去程查無可售車次或選購的車票已售完，請重新輸入訂票條件。"
                driver.quit()
                return ans
            else:
                print("sucess")
                break
        except:
            ans = "輸入錯誤"
            driver.quit()
            return ans

    #----------------------------

    #輸入基本資料訂票頁面
    r3 = driver.page_source
    soup3 = BeautifulSoup(r3, "html.parser")
    price = soup3.select_one('p#TotalPrice')
    departuretime = soup3.select_one('span#InfoDeparture0')
    arrivalime = soup3.select_one('span#InfoArrival0')
    # conn = mariadb.connect(host="127.0.0.1", port=3306, user="root", password="123456789",database="test")
    # conn = mariadb.connect(host="127.0.0.1", port=3306,
    #                       user="root", password="",
    #                       database="ticket_test")
    # cursor=conn.cursor()
    # id_user=session['id'] #取得使用者ID
    # cursor.execute(f"select nationid from account where id = '{id_user}' ")
    # nationid_user = cursor.fetchone()
    nationid_user = user_info["nationid"]  # 身分證字號，套登入介面後拿掉
    # cursor.execute(f"select phonenumber from account where id = '{id_user}' ")
    # phonenumber_user = cursor.fetchone()
    phonenumber_user = user_info["phonenumber"] # 手機號碼，套登入介面後拿掉
    driver.find_element(By.ID,"idNumber").send_keys(nationid_user)
    driver.find_element(By.ID,"mobilePhone").send_keys(phonenumber_user)
    driver.find_element(By.NAME,'agree').click()
    driver.find_element(By.ID,'isSubmit').click()
    sleep(1)
    try:    
        driver.find_element(By.ID,'btn-custom2').click()
        sleep(1)
        driver.find_element(By.ID,"BookingS3Form_TicketPassengerInfoInputPanel_passengerDataView_0_passengerDataView2_passengerDataIdNumber").send_keys(nationid_user)
        sleep(1)
        driver.find_element(By.ID,'isSubmit').click()
        sleep(1)
        driver.find_element(By.ID,'btn-custom2').click()
    except:
        print("notfindnewelement")
    print("sucess")
    sleep(3)
    #----------------------------

    #訂票頁面完成頁面
    r4=driver.page_source
    if "取票人資訊 請輸入正確之身分證字號" in r4:
        ans = "取票人資訊 請輸入正確之身分證字號"
        driver.quit()
        return ans
    elif "電話長度不得少於8" in r4:
        ans = "電話長度不得少於8"
        driver.quit()
        return ans
    else:
        soup4 = BeautifulSoup(r4, "html.parser")
        seat_code = soup4.select_one('p.pnr-code') #span
        price = price.text
        departuretime = departuretime.text
        arrivalime = arrivalime.text
        train_code = []
        print("訂位號碼在這裡", seat_code.text)
        ans = seat_code.text
        train_code.append(seat_code.text) 
        # seat=soup4.select('div.seat-label')
        # train_seat=[]
        # for s in seat:
        #     s=s.text
        #     s=s.strip('\n').split()
        #     for x in s:
        #         print(x,end=" ")
        #         train_seat.append(x)
        # sleep(600)
        driver.quit()
        return ans
        # return render_template("highspeedsearch.html",price=price,train_code=train_code,train_seat=train_seat,departuretime=departuretime,arrivalime=arrivalime)


if __name__ == "__main__":
    pass