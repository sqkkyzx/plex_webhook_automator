import os
import cgi
import json
from io import BytesIO
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request

from payload import Payload
from log import log, Color, WebSocket, connections
from pydantic import BaseModel

env = os.environ


class Environ:
    LOCALIZATION = bool(env.get('LOCALIZATION', True))
    PLEX_HOST = env.get('PLEX_HOST', 'host.docker.internal')
    PLEX_PORT = env.get('PLEX_PORT', '32400')
    PLEX_TOKEN = env.get('PLEX_TOKEN', '')
    PLEX_URL = f'http://{PLEX_HOST}:{PLEX_PORT}'


app = FastAPI()
app.mount("/admin/", StaticFiles(directory="html"), name="static")


@app.post("/event")
async def main(request: Request):
    body = await request.body()
    content_type = cgi.parse_header(request.headers.get('content-type'))[1]
    multipart_data = cgi.parse_multipart(
        fp=BytesIO(body),
        pdict={'boundary': bytes(content_type['boundary'], "utf-8")}
    )
    payload_json = multipart_data.get('payload', "{}")[0]
    log.debug(payload_json)

    payload = Payload(json.loads(payload_json))
    thumb = multipart_data.get('thumb', [None])[0]

    if thumb:
        filename = f"thumb/{payload.Metadata.ratingKey}.jpg"
        with open(filename, "wb") as thumb_file:
            thumb_file.write(thumb)

    match payload.TopLevel.event:
        case 'library.on.deck':
            pass
        case 'library.new':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} "
                     F"新增加了媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")
            if Environ.LOCALIZATION is True:
                import func_localization
                func_localization.PlexServer(Environ.PLEX_URL, Environ.PLEX_TOKEN).operate_item(
                    payload.Metadata.ratingKey)
        case 'media.play':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Green}{Color.ITALIC}开始播放{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")
        case 'media.pause':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Yellow}{Color.ITALIC}暂停播放{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")
        case 'media.resume':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Green}{Color.ITALIC}继续播放{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")
        case 'media.stop':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Red}{Color.ITALIC}停止播放{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")
        case 'media.scrobble':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Red}{Color.ITALIC}已看完{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET} ")
        case 'media.rate':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"用户 {Color.BOLD}{Color.Magenta}{payload.Account.title}{Color.RESET} "
                     F"将库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET} "
                     F"评为 {Color.Red}{Color.BOLD}{Color.ITALIC}{payload.Metadata.userRating}{Color.RESET} 分")
        case 'admin.database.backup':
            log.info(payload_json)
            pass
        case 'admin.database.corrupte':
            log.info(payload_json)
            pass
        case 'device.new':
            log.info(payload_json)
            pass
        case 'playback.started':
            log.info(F"服务器 {Color.BOLD}{Color.Magenta}{payload.Server.title}{Color.RESET} 的"
                     F"共享用户 {Color.BOLD}{Color.Magenta}{payload.Account.title} {Color.Green}{Color.ITALIC}开始播放{Color.RESET} "
                     F"库 {Color.BOLD}{Color.Magenta}{payload.Metadata.librarySectionTitle}{Color.RESET} 上的"
                     F"媒体 {Color.BOLD}{Color.Magenta}{payload.Metadata.title}{Color.RESET}")

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
    log.info(f'已新增标签 {Color.BOLD}{Color.Red}{tag.key}{Color.RESET} 的翻译 {Color.BOLD}{Color.Green}{tag.value}{Color.RESET}')
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


# ----------------TAGS----------------------


class Config(BaseModel):
    LOCALIZATION:bool = bool(env.get('LOCALIZATION', True))
    PLEX_HOST:str = env.get('PLEX_HOST', 'host.docker.internal')
    PLEX_PORT:int = env.get('PLEX_PORT', '32400')
    PLEX_TOKEN:str = env.get('PLEX_TOKEN', '')


@app.get("/api/config")
def get_config():
    if os.path.exists('config/config.json'):
        with open('config/config.json', 'r') as file:
            return json.load(file)
    else:
        default_config = Config()
        with open('config/config.json', 'w') as file:
            json.dump(default_config.model_dump(), file, ensure_ascii=False)
        return default_config.model_dump()


@app.put("/api/config")
def edit_config(cfg: Config):
    with open('config/config.json', 'w') as file:
        json.dump(cfg.model_dump(), file, ensure_ascii=False)
    log.info(f'更新了配置文件')
    return {"success": True}
