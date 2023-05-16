import datetime,time
import requests

day = datetime.datetime.now().strftime("%A") 

while day.lower() != "sunday":
    time.sleep(43200)
    continue

requests.post("http://127.0.0.1:8080/update_week", data={"username":"Kryotech_infirmary","password":"School_150"})