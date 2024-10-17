import requests
# from bs4 import BeautifulSoup
import time

#====================================

def _directions_api(departurE, arrivaL, departure_time):
    global total_list, jsoN
    #%%
    def _time(time_stamp):
        struct_time = time.localtime(time_stamp) # 轉成時間元組
        timeString = time.strftime("%m-%d %H:%M", struct_time) # 轉成字串
        time_day = time.strftime("%m-%d", struct_time) # 轉成字串
        time_today = time.strftime("%m-%d", time.localtime()) # 今天日期，轉成字串
        if time_day != time_today:
            week = {"Sunday": "星期日", 
                    "Monday": "星期一", 
                    "Tuesday": "星期二", 
                    "Wednesday": "星期三", 
                    "Thursday": "星期四", 
                    "Friday": "星期五", 
                    "Saturday": "星期六"}
            timeString += f"({week[time.strftime('%A', struct_time)]})"
        return timeString
        
    def _time_stamp(timeString):
        struct_time = time.strptime(timeString, "%Y-%m-%d %H:%M") # 轉成時間元組
        time_stamp = int(time.mktime(struct_time)) # 轉成時間戳
        return time_stamp
    
    
    myUrl = "https://maps.googleapis.com/maps/api/directions/json?"     #網址
    # 使用header
    myHeader = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
    # 使用 session
    
    time_stamp = _time_stamp(departure_time) # 時間格式為字串
    myParams = {"loading": "async",
              "region": "TW", 
              "language": "zh-TW",
              "destination": arrivaL,
              "origin": departurE,
              "mode": "transit",
              "departure_time": time_stamp, 
               "transitOptions": ["BUS"],
              "key": "AIzaSyDOcGLf8tlo5p-rN5TOshXNt7rShhiN4jo"
              }
    mySession = requests.Session()
    myHtml = mySession.get(myUrl, headers=myHeader, params=myParams)       #取得網頁html碼
    
    if myHtml.status_code == requests.codes.ok:
        # print("ok")
        # mySoup = BeautifulSoup(myHtml.text, "lxml")  #解析網頁html碼  #用"lxml"或"html5lib"均可
        jsoN = myHtml.json()
        # texT = myHtml.text
        
        way_list = []
        way_dict = {}
        total_list = jsoN["routes"][0]["legs"]
        way_dict["departure_time"] = _time(total_list[0]["departure_time"]["value"])
        way_dict["arrival_time"] = _time(total_list[0]["arrival_time"]["value"])
        way_dict["total_distance"] = total_list[0]["distance"]["text"]
        way_dict["total_duration"] = total_list[0]["duration"]["text"]
        way_list.append(way_dict)
    
        steps = total_list[0]["steps"]                        # 路線
        steps_list = []
        for ii in steps:
            steps_dict = {}
            steps_dict["travel_mode"] = "走路" if ii["travel_mode"] == "WALKING" else ii["html_instructions"].replace("長途列車", "臺鐵").replace("高速火車", "高鐵").split(" ")[0]
            steps_dict["distance"] = ii["distance"]["text"]
            steps_dict["duration"] = ii["duration"]["text"]
            steps_dict["instruction"] = ii["html_instructions"].replace("長途列車", "臺鐵").replace("高速火車", "高鐵")
            if ii["travel_mode"] == "WALKING":
                walk_list = []
                for walk in ii["steps"]:
                    walk_dict = {}
                    walk_dict["distance"] = walk["distance"]["text"]
                    walk_dict["duration"] = walk["duration"]["text"]
                    try:
                        walK = walk["html_instructions"].replace('<span class="location">', '').replace('</span>', ' ')
                        walK = walK.replace('<b>', '').replace('</b>', ' ').replace('<div style="font-size:0.9em">', ' ').replace('</div>', '').replace('<wbr/>', '')
                        walk_dict["route"] = walK
                    except:
                        pass
                    walk_list.append(walk_dict)
                steps_dict["step_detail"] = walk_list
                    
            else:
                detial_dict = {}
                detial_dict["departure_stop"] = ii["transit_details"]["departure_stop"]["name"].replace('高鐵', '').replace('站', '').replace('新左營', '左營')
                detial_dict["departure_time_show"] = _time(ii["transit_details"]["departure_time"]["value"])
                detial_dict["departure_time_year"] = time.strftime("%Y", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["departure_time_month"] = time.strftime("%m", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["departure_time_day"] = time.strftime("%d", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["departure_time_hour"] = time.strftime("%H", time.localtime(ii["transit_details"]["departure_time"]["value"]))
                detial_dict["departure_time_minute"] = time.strftime("%M", time.localtime(ii["transit_details"]["departure_time"]["value"]))
                detial_dict["arrival_stop"] = ii["transit_details"]["arrival_stop"]["name"].replace('高鐵', '').replace('站', '').replace('新左營', '左營')
                detial_dict["arrival_time_show"] = _time(ii["transit_details"]["arrival_time"]["value"])
                detial_dict["arrival_time_year"] = time.strftime("%Y", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["arrival_time_month"] = time.strftime("%m", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["arrival_time_day"] = time.strftime("%d", time.localtime(ii["transit_details"]["departure_time"]["value"])) 
                detial_dict["arrival_time_hour"] = time.strftime("%H", time.localtime(ii["transit_details"]["departure_time"]["value"]))
                detial_dict["arrival_time_minute"] = time.strftime("%M", time.localtime(ii["transit_details"]["departure_time"]["value"]))
                try:
                    detial_dict["transit_number"] = ii["transit_details"]["trip_short_name"]  # 火車 、 高鐵
                except:
                    pass
                detial_dict["transit_name"] = ii["transit_details"]["line"]["name"]   
                steps_dict["transit_detail"] = detial_dict
            
            
            
            steps_list.append(steps_dict)
    
        way_list.append(steps_list)
    
    #%%
        # 列印
        # print(way_list[0])
        # print("*"*30)
        # print()
        # for _ in way_list[1]:
        #     print(_)
        #     print("="*30)
    #%%
        return way_list


#====================================
if __name__ == "__main__":
    departurE = "台中車站"
    # starT = "24.2611458,120.7250903"
    arrivaL = "台北車站"
    departure_time = "2024-10-16 10:30"
    way_list = _directions_api(departurE, arrivaL, departure_time)
    
    # print(way_list[0])
    # print("*"*30)
    # print()
    # for _ in way_list[1]:
    #     print(_)
    #     print("="*30)
