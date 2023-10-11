
# major credit to https://github.com/qwweerdf/Visa-Slot-Checker/blob/main/main.py
# reschedule function credit to https://github.com/uxDaniel/visa_rescheduler/blob/fe0cd0ac585f6a52c3a7a947ebd4f1a9125bc5df/visa.py#L163
import requests
from bs4 import BeautifulSoup
import datetime
import time
import json
    
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42' 
email = 'zxu.xu@mail.utoronto.ca'
password = 'nevdo6-kahVoc-xokjex'
scheduleID = '44676732'
log_file = open("log.txt", "a")

def isUnderMaint():
    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'Cache-Control': 'max-age=0',
    #     'Connection': 'keep-alive',
    #     'Host': 'ais.usvisa-info.com',
    #     'If-None-Match': 'W/"cf55a01c5ef60ca87aaf8b7f547bd746"',
    #     'sec-ch-ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'Upgrade-Insecure-Requests': '1',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.42'
    # }
    print(userAgent)
    isUnderMaint = True
    log('check whether the site is live')
    while isUnderMaint:
        site_response = requests.Session().get('https://ais.usvisa-info.com/', headers=userAgent)
        print(site_response.status_code)
        if site_response.status_code == 503:
            log('site is under maintenance. Check back in 5 mins')
        elif site_response.status_code == 200:
            log('site is live.')
            isUnderMaint = False 
        else:
            log('unknow status. check bacin in 5 mins.'+ str(site_response.status_code))
        if isUnderMaint:
            time.sleep(300)

# send login request, and gain cookie after login. (发送登录请求，获取登录后的cookie)
def login(email, password):
    isUnderMaint()
    log('Start login')
    # Get authtoken and cookies
    response_login = requests.Session().get('https://ais.usvisa-info.com/en-ca/niv/users/sign_in', headers={'User-Agent': userAgent})
    soup = BeautifulSoup(response_login.text, 'lxml')
    authToken = soup.find_all('input')[1].attrs['value']
    CSRFToken = soup.find_all('meta')[6].attrs['content']
    # Prepare cookies string for login
    cookie_login = '_yatri_session=' + response_login.cookies.get('_yatri_session')

    # new header and payload is required on 2022-11-17 morning.
    # payload = {
    #     'utf8': '✓',
    #     'user[email]': email,
    #     'user[password]': password,
    #     'policy_confirmed': '1',
    #     'commit': 'Sign In',
    #     'authenticity_token': authToken
    # }
    # headers = {  
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'Host': 'ais.usvisa-info.com',
    #     'Origin': 'https://ais.usvisa-info.com',
    #     'Referer': 'https://ais.usvisa-info.com/en-ca/niv/users/sign_in',
    #     'Update-Insecure-Requests': '1',
    #     'User-Agent': userAgent,
    #     'Cookie': cookie_login
    # }

    # 请请求头尽可能模拟浏览器
    payload = {
        'utf8': '✓',
        'user[email]': email,
        'user[password]': password,
        'policy_confirmed': '1',
        'commit': 'Sign In'
    }
    headers = {
        'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'ais.usvisa-info.com',
        'Origin': 'https://ais.usvisa-info.com',
        'Referer': 'https://ais.usvisa-info.com/en-ca/niv/users/sign_in',
        'User-Agent': userAgent,
        'Cookie': cookie_login,
        'X-CSRF-Token': CSRFToken,
        'X-Requested-With': 'XMLHttpRequest'
    }

    response_account = requests.Session().post('https://ais.usvisa-info.com/en-ca/niv/users/sign_in', headers=headers, data=payload)
    # post can have cookies in response
    cookie_account = '_yatri_session=' + response_account.cookies.get('_yatri_session')
    log('Successful login.')
    return cookie_account

def log(txt):
    current = datetime.datetime.now()
    if type(txt) != str:
        txt = str(txt)
    print(str(current) + " | " + txt)
    log_file.write(str(current) + " | " + txt + "\n")

def reschedule(cookie, date, time):
    log('Get authtoken for reschedule')
    headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                    'Connection': 'keep-alive',
                    'Cookie': cookie,
                    'Host': 'ais.usvisa-info.com',
                    'Referer': 'https://ais.usvisa-info.com/en-ca/niv/schedule/'+ scheduleID + '/appointment',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': userAgent
            }
    response_appointment = requests.Session().get('https://ais.usvisa-info.com/en-ca/niv/schedule/'+ scheduleID + '/appointment', headers=headers)
    # log(response_appointment.text)
    soup = BeautifulSoup(response_appointment.text, 'lxml')
    authToken = soup.find_all('meta')[6].attrs['content']
    cookie = '_yatri_session=' + response_appointment.cookies.get('_yatri_session')

    log('Start reschedule')
    payload = {
        "utf8": '✓',
        "authenticity_token": authToken,
        "confirmed_limit_message": '1',
        "use_consulate_appointment_capacity": 'true',
        "appointments[consulate_appointment][facility_id]": '94',
        "appointments[consulate_appointment][date]": date,
        "appointments[consulate_appointment][time]": time,
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'ais.usvisa-info.com',
        'Origin': 'https://ais.usvisa-info.com',
        'Referer': 'https://ais.usvisa-info.com/en-ca/niv/schedule/'+ scheduleID + '/appointment',
        'Update-Insecure-Requests': '1',
        "User-Agent": userAgent,
        "Cookie": cookie
    }
    response_reschedule = requests.Session().post('https://ais.usvisa-info.com/en-ca/niv/schedule/'+ scheduleID + '/appointment', headers=headers, data=payload)
    log(response_reschedule.text)

    if response_reschedule.status_code == 200 and response_reschedule.text.__contains__('successfully scheduled'):
        log('Rescheduled Successfully! date=' + date + '; time=' + time)
        return cookie, date
    else: 
        log('Reschedule Failed. date=' + date + '; time=' + time)
        return cookie, ''
        

if __name__ == '__main__':


    # User Inputs
    # Max number of runs each time is 70 before being blocked.
    sleepTime = 30 #secs
    number_of_runs = 40
    interval_run = 61 #mins

    # System Inputs
    current_file = open("current.txt", "r")
    currentDate = current_file.readline()
    current_file.close()
    nextRunTime = datetime.datetime.now()
    count_error = 0

    # Start execute
    cookie = login(email, password)
    while True and count_error < 11:
        count_run = 0
        try:
            while((datetime.datetime.now() > nextRunTime) and (count_run < number_of_runs)):
                count_run += 1
                log('Checking earlier date.')
                headers = {
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                        'Cookie': cookie,
                        'Connection': 'keep-alive',
                        'Host': 'ais.usvisa-info.com',
                        'Referer': 'https://ais.usvisa-info.com/en-ca/niv/schedule/'+ scheduleID + '/appointment',
                        'User-Agent': userAgent
                }
                response_reschedule = requests.Session().get("https://ais.usvisa-info.com/en-ca/niv/schedule/" + scheduleID + "/appointment/days/94.json?appointments[expedite]=false", headers=headers)
                # response_reschedule.text is [{"date":"2024-02-08","business_day":true},{"date":"2024-02-09","business_day":true}]
                earliestDate = response_reschedule.text[10:20]
                cookie = '_yatri_session=' + response_reschedule.cookies.get('_yatri_session')

                if len(response_reschedule.text) < 10:
                    log("No slot available. "  + response_reschedule.text)
                    count_run = number_of_runs
                elif earliestDate == "Your sessi" or earliestDate == "You need t":
                    log("Session time out. " + response_reschedule.text)
                    cookie = login(email, password)
                elif earliestDate < currentDate:
                    # Find available time
                    response_reschedule_times = requests.Session().get("https://ais.usvisa-info.com/en-ca/niv/schedule/" + scheduleID + "/appointment/times/94.json?date=" + earliestDate + "&appointments[expedite]=false", headers=headers)
                    # {"available_times":["07:45","08:00","08:15","08:30","08:45","09:15","09:30","09:45","10:15","11:15"],"business_times":["07:45","08:00","08:15","08:30","08:45","09:15","09:30","09:45","10:15","11:15"]}
                    earliestDate_time = response_reschedule_times.text[21:26]
                    log("Earlier date is found. earliestDate=" + earliestDate + " " + earliestDate_time + "; currentDate=" + currentDate)
                    cookie, date = reschedule(cookie, earliestDate, earliestDate_time)
                    if date != '':
                        currentDate = date
                        current_file = open("current.txt", "w")
                        current_file.write(date)
                        current_file.close()
                else:
                    log("Earlier time was not found. earliestDate=" + earliestDate + "; currentDate=" + currentDate)

                # sleep time (少于5秒可能会造成TooManyRequests Error,建议sleep时间>=5秒)
                time.sleep(sleepTime)
            if count_run != 0:
                nextRunTime = datetime.datetime.now() + datetime.timedelta(minutes=interval_run)
                count_run = 0
            log('it is not time to hammer system again. Going sleep for 5 mins.')
            time.sleep(300)
        except Exception as e:
                log('Error: ')
                log(str(e.__class__))
                log(str(e))
                authToken, cookie = login(email, password)
                count_error += 1
                count_run = 0