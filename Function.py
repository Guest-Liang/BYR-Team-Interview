import requests
import time
import loguru

Url = "http://127.0.0.1:1323"
Token = None
LastLoginTime = None
WaitTimeAfter401 = 15  # code 401后等待15秒
loguru.logger.add(sink="./runtime.log", format="{time} | {level} | {message}", level="DEBUG")

# 登录
def Login():
    global Token
    UserName = "GuestLiang"

    # 获取密码
    response = requests.post(f"{Url}/signup", data={"username": UserName})
    if response.status_code == 200:
        PassWord = response.json()["password"]
        loguru.logger.info(f"Received password: {PassWord}")
    else:
        loguru.logger.error(f"Received status_code {response.status_code}: {response.text}")
        loguru.logger.error("Failed to get password.")
        return

    response = requests.post(f"{Url}/login", data={"username": UserName, "password": PassWord})
    if response.status_code == 200:
        Token = response.json()["token"]
        loguru.logger.info(f"Get token successfully: {Token}")
    else:
        loguru.logger.error(f"Received status code {response.status_code}: {response.text}")
        loguru.logger.error("Login failed")


# Token心跳
def HeartBeat():
    global Token
    if Token:
        headers = {"Authorization": f"Bearer {Token}"}
        try:
            response = requests.get(f"{Url}/api/heartbeat", headers=headers)
            if response.status_code == 200:
                NewToken = response.json()["token"]
                if NewToken != Token:
                    loguru.logger.info(f"Token refreshed: {NewToken}")
                    Token = NewToken
            else:
                HandleError(response)
        except requests.exceptions.RequestException as e:
            loguru.logger.exception(f"Connection error: {e}")
            loguru.logger.info("Waiting 2s...")
            time.sleep(2)  # 等待2秒


# 拿一下Code
def getCode():
    global Token
    if Token:
        headers = {"Authorization": f"Bearer {Token}"}
        try:
            response = requests.get(f"{Url}/api/info", headers=headers)
            if response.status_code == 200:
                code = response.json()["code"]
                loguru.logger.info(f"Received code: {code}")
                return code
            else:
                HandleError(response)
        except requests.exceptions.RequestException as e:
            loguru.logger.exception(f"Connection error: {e}")
            loguru.logger.info("Waiting 2s...")
            time.sleep(2)  # 等待2秒
    return None


# 提交
def Validate(code):
    global Token
    if Token and code:
        headers = {"Authorization": f"Bearer {Token}"}
        try:
            response = requests.post(f"{Url}/api/validate", headers=headers, data={"code": code})
            if response.status_code == 200:
                loguru.logger.info(f"Validation successful. Server response: {response.text}")
            else:
                HandleError(response)
        except requests.exceptions.RequestException as e:
            loguru.logger.exception(f"Connection error: {e}")
            loguru.logger.info("Waiting 2s...")
            time.sleep(2)  # 等待2秒


# 处理不同状态码
def HandleError(response):
    StatusCode = response.status_code
    ErrorMessage = response.text

    if StatusCode == 401:
        if "missing or malformed jwt" in ErrorMessage:  # 没加上bearer前缀会出现的
            loguru.logger.error("JWT is missing or malformed")
        elif "invalid or expired jwt" in ErrorMessage:
            loguru.logger.error(f"{StatusCode}: JWT is invalid or expired")
            if LastLoginTime is None or (time.time() - LastLoginTime > WaitTimeAfter401):
                Login()  # 重新获取令牌
            else:
                time.sleep(WaitTimeAfter401 - (time.time() - LastLoginTime))  # 等待一段时间
    elif StatusCode == 403:
        loguru.logger.error(f"{StatusCode}: Forbidden")
    elif StatusCode == 404:
        loguru.logger.error(f"{StatusCode}: Not Found")
    elif StatusCode == 405:
        loguru.logger.error(f"{StatusCode}: Method not allowed")
    elif StatusCode == 418:
        loguru.logger.error(f"{StatusCode}: I'm a teapot")
    elif StatusCode == 502:
        loguru.logger.error(f"{StatusCode}: Bad Gateway")
        return False  # 服务可能下线
    else:
        loguru.logger.error(f"Received status code {StatusCode}: {ErrorMessage}")
    return True  # 服务在线


if __name__ == "__main__":
    Login()  # 初始登录一次
    LastCode = None
    StartTime = time.time()
    while time.time() - StartTime < 300:  # 5分钟
        HeartBeat()  # 更新Token
        Code = getCode()  # 获取要提交的Code
        if Code and Code != LastCode:  # 有更新才提交
            Validate(Code)  # 提交验证
            LastCode = Code
        else:
            loguru.logger.info("Code didn't change, waiting 5s...")
        time.sleep(5)  # 都等5s
    loguru.logger.info("Program finished after 5 minutes.")
