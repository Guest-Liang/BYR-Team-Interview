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
        return

    # 拿Token
    response = requests.post(f"{Url}/login", data={"username": UserName, "password": PassWord})
    if response.status_code == 200:
        Token = response.json()["token"]
        print("Logged in successfully with token:", Token)
    else:
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
            return
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
           return

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
