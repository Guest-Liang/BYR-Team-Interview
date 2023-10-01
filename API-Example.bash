# 获取对应用户名密码 username名字可以随便取 笔者id是Ts2
curl 127.0.0.1:1323/signup -d "username=Ts2"
{"password":"4b65e3b52d","username":"Ts2"}

# 使用获取到的密码登录获得token，token用于接下来的api鉴权使用
curl 127.0.0.1:1323/login -d "username=Ts2&password=4b65e3b52d"
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVHMyIiwiZXhwIjoxNjk1NjE5ODE4fQ.pE87ZmJc5QmVpBtEiG4a0P_OVdSiD2XyNhzyHNNjL_Y"}

# heartbeat用于更新目前用户的token(因为token是有时效性的，在不重复登录的情况下更新token就用这个api)
curl 127.0.0.1:1323/api/heartbeat -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVHMyIiwiZXhwIjoxNjk1NjE5ODE4fQ.pE87ZmJc5QmVpBtEiG4a0P_OVdSiD2XyNhzyHNNjL_Y"
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVHMyIiwiZXhwIjoxNjk1NjE5OTI1fQ.TNReLlRAFs_EBF168cbt-MSwBH1uriwXXRzEtt0JRTw"}

# 获取要提交的内容
curl 127.0.0.1:1323/api/info -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVHMyIiwiZXhwIjoxNjk1NjE5ODE4fQ.pE87ZmJc5QmVpBtEiG4a0P_OVdSiD2XyNhzyHNNjL_Y"
{"code":"79db02dec4"}

# 提交
curl 127.0.0.1:1323/api/validate -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiVHMyIiwiZXhwIjoxNjk1NjE5ODE4fQ.pE87ZmJc5QmVpBtEiG4a0P_OVdSiD2XyNhzyHNNjL_Y" -d "code=79db02dec4"
"OK"

# ----------------------------------------
# 需要处理的状态码：试出来的，没试出来暂时不管（
{
    "200":"OK",
    "401":"[missing or malformed jwt] or [invalid or expired jwt] or [Unauthorized]",
    "403":"forbidden",
    "404":"Not Found",
    "405":"Method not allowed",
    "418":"NOPE",
    "502":"Bad Gateway"
}