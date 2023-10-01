import requests
import time

Url = "http://127.0.0.1:1323"
Token = None

# 登录
def Login():
    global Token
    UserName = "GuestLiang"
    
    # 获取密码
    response = requests.post(f"{Url}/signup", data={"username": UserName})
    if response.status_code == 200:
        PassWord = response.json()["password"]
        print("Received password:", PassWord)
    else:
        print(f"Received status_code {response.status_code}: {response.text}")
        print("Failed to get password.")
        return

    # 拿Token
    response = requests.post(f"{Url}/login", data={"username": UserName, "password": PassWord})
    if response.status_code == 200:
        Token = response.json()["token"]
        print("Logged in successfully with token:", Token)
    else:
        print(f"Received status code {response.status_code}: {response.text}")
        print("Login failed")

# Token心跳
def HeartBeat():
    global Token
    if Token:
        headers = {"Authorization": f"Bearer {Token}"}
        response = requests.get(f"{Url}/api/heartbeat", headers=headers)
        if response.status_code == 200:
            NewToken = response.json()["token"]
            if NewToken != Token:
                print("Token refreshed:", NewToken)
                Token = NewToken
        else:
            HandleError(response)
            return

# 拿一下Code
def getCode():
    global Token
    if Token:
        headers = {"Authorization": f"Bearer {Token}"}
        response = requests.get(f"{Url}/api/info", headers=headers)
        if response.status_code == 200:
            code = response.json()["code"]
            print("Received code:", code)
            return code
        else:
            HandleError(response)
            return

# 提交
def Validate(code):
    global Token
    if Token and code:
        headers = {"Authorization": f"Bearer {Token}"}
        response = requests.post(f"{Url}/api/validate", headers=headers, data={"code": code})
        if response.status_code == 200:
            print("Validation successful")
        else:
           HandleError(response)
           return

# 处理不同状态码
def HandleError(response):
    StatusCode = response.status_code
    ErrorMessage = response.text

    if StatusCode == 401:
        print("invalid or expired jwt, refreshing token...")
        Login()  # 重新获取Token
    elif StatusCode == 403:
        print(f"{StatusCode}: Forbidden")
    elif StatusCode == 405:
        print(f"{StatusCode}: Method not allowed")
    elif StatusCode == 502:
        print(f"{StatusCode}: Bad Gateway - Service may be offline, waiting for recovery...")
        return False  # 服务可能下线
    else:
        print(f"Received status code {StatusCode}: {ErrorMessage}")
    return True  # 服务仍然在线

if __name__ == "__main__":
    Login()  # 初始登录一次
    LastCode = None
    StartTime = time.time()
    while time.time() - StartTime < 300:  # 5分钟
        HeartBeat()  # 更新Token
        Code = getCode()  # 获取要提交的Code
        if Code and Code != LastCode: # 有更新才提交
            Validate(Code)  # 提交验证
            LastCode = Code 
        else:
            time.sleep(5) # 没更新等5s

        time.sleep(10)  # 10s来一次

    print("Program finished after 5 minutes.")
    exit()
