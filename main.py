import imp
from fastapi import FastAPI, Request, Response


from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException

from api.hefeng import get_city_weather

app = FastAPI()

token = 'e17d6e0e603e49618b5ffe6224ba1444'

@app.get("/")
async def main(signature, echostr, timestamp, nonce):
    try:
        check_signature(token, signature, timestamp, nonce)
    except InvalidSignatureException:
        return 'error'
    return int(echostr)

@app.post("/")
async def wechat(request: Request, response: Response):
    content = await request.body()
    msg = parse_message(content)
    if msg.content == "hello":
        reply = create_reply("world", msg)
        return reply.render()

    if msg.content[0:5] == "实时天气 " or msg.content == "实时天气":
        res = get_city_weather(city_name=msg.content[5:] if msg.content[5:] else "郑州", now=True)
        if res:
            info = res['now']
            res = "观测时间: {}\n当前温度: {}\n体感温度: {}\n天气: {}\n风向: {}\n风力: {}\n相对湿度(%): {}\n".format(
                info['obsTime'][0: 10] + ' ' + info['obsTime'][11: 16],
                info['temp'],
                info['feelsLike'],
                info['text'],
                info['windDir'],
                info['windScale'],
                info['humidity'])
            reply = create_reply(res, msg)
            return Response(reply.render(), media_type="application/xml")
        else:
            reply = create_reply("请输入正确的城市名称", msg)
            return Response(reply.render(), media_type="application/xml")

    if msg.content[0:3] == "天气 " or msg.content == "天气":
        res = get_city_weather(city_name=msg.content[3:] if msg.content[3:] else "郑州")
        if res:
            info = ""
            for i in res['daily']:
                text = "日期: {}\n最高温度: {}\n最低温度: {}\n天气: {}\n相对湿度: {}\n\n".format(i['fxDate'], i['tempMax'],
                                                                                    i['tempMin'],
                                                                                    i['textDay'], i['humidity'])
                info += text
            reply = create_reply(info, msg)
            return Response(content=reply.render(), media_type="application/xml")

        else:
            reply = create_reply("请输入正确的城市名称", msg)
            return Response(reply.render(), media_type="application/xml")


