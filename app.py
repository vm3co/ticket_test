# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 12:55:56 2021

@author: Alvin
"""

from flask import Flask, request, redirect, url_for, render_template
import os, datetime
from Directions_API_html import _directions_api
from highspeedrail import _hsrsearch

app = Flask(__name__)

@app.route("/", methods=['GET', "POST"])
def _begin():
    return redirect(url_for('_map'))

@app.route("/index", methods=['GET', "POST"])
def _login():
    return redirect(url_for('_map'))

@app.route("/map", methods=['GET', "POST"])
def _map():
    tt = datetime.datetime.today() # 抓取目前時間
    todaY = tt.strftime("%Y-%m-%d")
    todaY_time = tt.strftime("%H:%M")
    # todaY_hour = int(tt.strftime("%H"))+8
    # todaY_minute = int(tt.strftime("%M"))
    # todaY_time = f"{todaY_hour}:{todaY_minute}"
    if request.method == "GET":
        error_text = ""
        return render_template("input.html", todaY=todaY, todaY_time=todaY_time, error_text=error_text)
    else:
        # 抓定位
        gpS = request.form["latitude"]+", "+request.form["longitude"]
        departurE = gpS if request.form["departure"] == "我的目前位置" else request.form["departure"]
        arrivaL = gpS if request.form["arrival"] == "我的目前位置" else request.form["arrival"]
        # 出發時間
        departure_day = request.form["departure_day"]
        departure_time = request.form["departure_time"]
        if int(departure_day.split("-")[0]) < int(tt.strftime("%Y")) or int(departure_day.split("-")[1]) < int(tt.strftime("%m")) or int(departure_day.split("-")[2]) < int(tt.strftime("%d")):
            error_text = "日期不可小於今日"
            return render_template("input.html", todaY=todaY, todaY_time=todaY_time, error_text=error_text, departurE=request.form["departure"], arrivaL=request.form["arrival"])
        elif departure_day == tt.strftime("%Y-%m-%d") and (int(departure_time.split(":")[0]) < int(tt.strftime("%H")) or int(departure_time.split(":")[1]) < int(tt.strftime("%M"))):
            error_text = "時間不可小於目前時間"
            return render_template("input.html", todaY=todaY, todaY_time=todaY_time, error_text=error_text, departurE=request.form["departure"], arrivaL=request.form["arrival"])
        departure_time = departure_day +" "+ departure_time
        
        # 呼叫google地圖api函式
        way_list = _directions_api(departurE, arrivaL, departure_time)  
        # return render_template("way.html", way_list=way_list, starT=starT, arrivaL=arrivaL, traffic=traffic_list_chi[int(traffiC)])
        return render_template("Directions_API_html.html", way_list=way_list, departurE=departurE, arrivaL=arrivaL)
        # return traffiC

@app.route("/railway", methods=['GET', "POST"])
def _train():
    if request.method == "POST":
        return "臺鐵"

# 高鐵
@app.route("/hsr", methods=['GET', "POST"])
def _hsr():
    global transit_detail
    if request.method == "POST":
        transit_detail = eval(request.form["transit_detail"])
        print(transit_detail)
        return render_template("highspeedsearch.html", transit_detail=transit_detail)
    else:
        return redirect(url_for('_map'))

@app.route("/hsr/search", methods=['GET', "POST"])
def _hsr_search():
    if request.method == "POST":
        transit_detail = eval(request.form["transit_detail"])
        hsr_search_ticket = {}
        hsr_search_ticket["ft"] = request.form["fullticket"] # 全票
        hsr_search_ticket["ct"] = request.form["chileticket"] # 孩童票
        hsr_search_ticket["lt"] = request.form["loveticket"] # 愛心票
        hsr_search_ticket["ot"] = request.form["oldticket"] # 敬老票
        hsr_search_ticket["colt"] = request.form["collegeticket"] # 大學生票
        user_info = {}
        user_info["nationid"] = request.form["nationid"] # 身分證字號，套登入介面後拿掉
        user_info["phonenumber"] = request.form["phonenumber"] # 手機號碼，套登入介面後拿掉
        user_info["headless"] = request.form["headless"] # 測試無頭模式
        ans = _hsrsearch(transit_detail, hsr_search_ticket, user_info)
        
        if ans.isdigit():
            ans+="，完成訂票"
            return f'''
           <form action = "" method = "post">
              <h1 style="color:Tomato;">{ans}</h1>
              <a href="/index" style="display: inline-block; padding: 5px 10px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">回首頁
              </a>
              <a href="https://irs.thsrc.com.tw/IMINT/?wicket:bookmarkablePage=:tw.com.mitac.webapp.thsr.viewer.History" target="_blank" style="display: inline-block; padding: 5px 10px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">付款or取消
              </a>
           </form>
           '''
        return render_template("highspeedsearch.html", ans=ans, transit_detail=transit_detail) # ans就是答案喔
    else:
        return redirect(url_for('_map'))

@app.route("/bus", methods=['GET', "POST"])
def _bus():
    if request.method == "POST":
        return "公車"



if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(debug=False)
    # http://127.0.0.1:5000/
    
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', debug=False, port=port)
    
    
    