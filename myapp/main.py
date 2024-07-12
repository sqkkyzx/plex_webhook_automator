import json
import os
from datetime import datetime, timedelta

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from log import log, Color, WebSocket, connections
from payload import Payload


def config():
    if os.path.exists('config/config.json'):
        with open('config/config.json', 'r') as file:
            return json.load(file)
    else:
        default_config = {
            "LOCALIZATION": bool(os.environ.get('LOCALIZATION', True)),
            "PLEX_HOST": os.environ.get('PLEX_HOST', 'host.docker.internal'),
            "PLEX_PORT": int(os.environ.get('PLEX_PORT', '32400')),
            "PLEX_TOKEN": os.environ.get('PLEX_TOKEN', '{INPUT_YOUR_TOKEN'),
            "WEIBO_APP_KEY": "",
            "WEIBO_APP_SECRET": "",
            "WEIBO_REDIRECT_URL": "http://{INPUT_YOUR_HOST:POST}/api/weibo/oauth2",
            "WEIBO_ACCESS_TOKEN": "",
            "WEIBO_ACCESS_EXPIRES_DATE": ""
        }
        with open('config/config.json', 'w') as file:
            json.dump(default_config, file, ensure_ascii=False)
        return default_config


class Config(BaseModel):
    LOCALIZATION: bool
    PLEX_HOST: str
    PLEX_PORT: int
    PLEX_TOKEN: str
    WEIBO_APP_KEY: str
    WEIBO_APP_SECRET: str
    WEIBO_REDIRECT_URL: str
    WEIBO_ACCESS_TOKEN: str
    WEIBO_ACCESS_EXPIRES_DATE: str


app = FastAPI()
app.mount("/admin/", StaticFiles(directory="html"), name="static")


@app.post("/event")
async def main(request: Request):
    form = await request.form()
    payload = form.get('payload')
    # thumb = form.get('thumb')

    log.debug(payload)

    payload = Payload(json.loads(payload))

    # if thumb:
    #     filename = f"thumb/{payload.Metadata.ratingKey}.jpg"
    #     with open(filename, "wb") as thumb_file:
    #         thumb_file.write(thumb)

    server_log = F" {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} "
    user_log = F" {Color.BOLD}{Color.Magenta}{payload.Account.title}{Color.RESET} "
    library_log = F" {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} "
    meida_log = F" {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET} "
    rating_log = F" {Color.Red}{Color.BOLD}{Color.ITALIC}{payload.Metadata.userRating}{Color.RESET} "
    player_log = F" {Color.BOLD}{Color.Magenta}{payload.Player.title} "
    play_log = F" {Color.Green}{Color.ITALIC}开始播放{Color.RESET} "
    pause_log = F" {Color.Yellow}{Color.ITALIC}暂停播放{Color.RESET} "
    resume_log = F" {Color.Green}{Color.ITALIC}继续播放{Color.RESET} "
    stop_log = F" {Color.Red}{Color.ITALIC}停止播放{Color.RESET} "
    scrobble_log = F" {Color.Red}{Color.ITALIC}已看完{Color.RESET} "

    match payload.TopLevel.event:
        case 'library.on.deck':
            pass
        case 'library.new':
            log.info(F"服务器{server_log}的库{library_log}新增加了媒体{meida_log}")
            try:
                cfg = config()
                if cfg.get('LOCALIZATION') is True:
                    import func_localization
                    func_localization.PlexServer(
                        f"http://{cfg.get('PLEX_HOST')}:{cfg.get('PLEX_PORT')}", cfg.get('PLEX_TOKEN')
                    ).operate_item(payload.Metadata.ratingKey)
            except Exception as e:
                log.error(e)

        case 'media.play':
            log.info(F"服务器{server_log}的用户{play_log}库{library_log}上的媒体{meida_log}")
        case 'media.pause':
            log.info(F"服务器{server_log}的用户{user_log}{pause_log}库{library_log}上的媒体{meida_log}")
        case 'media.resume':
            log.info(F"服务器{server_log}的用户{resume_log}库{library_log}上的媒体{meida_log}")
        case 'media.stop':
            log.info(F"服务器{server_log}的用户{user_log}{stop_log}库{library_log}上的媒体{meida_log}")
        case 'media.scrobble':
            log.info(F"服务器{server_log}的用户{user_log}{scrobble_log}库{library_log}上的媒体{meida_log}")
        case 'media.rate':
            log.info(F"服务器{server_log}的用户{user_log}将库{library_log}上的媒体{meida_log}评为{rating_log}分")
        case 'admin.database.backup':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 已备份数据库")
        case 'admin.database.corrupte':
            log.info(payload)
        case 'device.new':
            log.info(F"设备{player_log}加入了服务器{server_log}")
        case 'playback.started':
            log.info(F"服务器{server_log}的共享用户{play_log}库{library_log}上的媒体{meida_log}")

    return 'succes'


@app.websocket("/ws_log")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open
    except Exception as e:
        log.error(e)
        connections.remove(websocket)


# ----------------TAGS----------------------


class TagTranlate(BaseModel):
    key: str = None
    value: str = None


@app.get("/api/tags")
def get_tags():
    with open('config/func_localization_tags.json', 'r') as file:
        return json.load(file)


@app.post("/api/tags")
def add_tag(tag: TagTranlate):
    with open('config/func_localization_tags.json', 'r') as file:
        tags = json.load(file)
    tags[tag.key] = tag.value
    with open('config/func_localization_tags.json', 'w') as file:
        json.dump(tags, file, ensure_ascii=False)
    log.info(
        f'已新增标签 {Color.BOLD}{Color.Red}{tag.key}{Color.RESET} 的翻译 {Color.BOLD}{Color.Green}{tag.value}{Color.RESET}')
    return {"success": True}


@app.delete("/api/tags")
def delete_tag(tag: TagTranlate):
    with open('config/func_localization_tags.json', 'r') as file:
        tags = json.load(file)
    if tag.key in tags:
        del tags[tag.key]
        with open('config/func_localization_tags.json', 'w') as file:
            json.dump(tags, file, ensure_ascii=False)
        log.info(f'已删除标签 {Color.BOLD}{Color.Red}{tag.key}{Color.RESET} 的翻译')
        return {"success": True}
    else:
        return {"success": False}


# ----------------CONFIG----------------------


@app.get("/api/config")
def get_config():
    return config()


@app.put("/api/config")
def edit_config(cfg: Config):
    with open('config/config.json', 'w') as file:
        json.dump(cfg.model_dump(), file, ensure_ascii=False)
    log.info(f'更新了配置文件')
    return {"success": True}


# ----------------WEIBO CONFIG----------------------

@app.get("/api/weibo/init")
def weibo_init():
    cfg = config()
    client_id = cfg.get('WEIBO_APP_KEY')
    redirect_uri = cfg.get('WEIBO_REDIRECT_URL')
    return RedirectResponse(
        url=f"https://api.weibo.com/oauth2/authorize?"
            f"response_type=code&client_id={client_id}&redirect_uri={redirect_uri}",
        status_code=302)


@app.get("/api/weibo/oauth2")
def weibo_oauth2(code):
    cfg = config()
    res = requests.post(
        'https://api.weibo.com/oauth2/access_token',
        params={
            'client_id': cfg.get('WEIBO_APP_KEY'),
            'client_secret': cfg.get('WEIBO_APP_SECRET'),
            'redirect_uri': cfg.get('WEIBO_REDIRECT_URL'),
            'code': code,
            'grant_type': 'authorization_code'
        }
    ).json()
    res['expires_date'] = (datetime.now() + timedelta(seconds=res['expires_in'])).strftime('%Y-%m-%d %H:%M')
    cfg['WEIBO_ACCESS_TOKEN'] = res["access_token"]
    cfg['WEIBO_ACCESS_EXPIRES_DATE'] = res["expires_date"]
    with open('config/config.json', 'w') as file:
        json.dump(cfg, file, ensure_ascii=False)
    return res


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=60014, reload=True, use_colors=True)
