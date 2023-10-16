import os
import cgi
import json
from io import BytesIO
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from pydantic import BaseModel

from payload import Payload
from log import log, WebSocket, connections
from log import Color as C
from typing import Dict

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
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} "
                     F"新增加了媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")
            if Environ.LOCALIZATION is True:
                import func_localization
                func_localization.PlexServer(Environ.PLEX_URL, Environ.PLEX_TOKEN).operate_item(
                    payload.Metadata.ratingKey)
        case 'media.play':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Green}{C.ITALIC}开始播放{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")
        case 'media.pause':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Yellow}{C.ITALIC}暂停播放{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")
        case 'media.resume':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Green}{C.ITALIC}继续播放{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")
        case 'media.stop':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Red}{C.ITALIC}停止播放{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")
        case 'media.scrobble':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Red}{C.ITALIC}已看完{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET} ")
        case 'media.rate':
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"用户 {C.BOLD}{C.Magenta}{payload.Account.title}{C.RESET} "
                     F"将库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET} "
                     F"评为 {C.Red}{C.BOLD}{C.ITALIC}{payload.Metadata.userRating}{C.RESET} 分")
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
            log.info(F"服务器 {C.BOLD}{C.Magenta}{payload.Server.title}{C.RESET} 的"
                     F"共享用户 {C.BOLD}{C.Magenta}{payload.Account.title} {C.Green}{C.ITALIC}开始播放{C.RESET} "
                     F"库 {C.BOLD}{C.Magenta}{payload.Metadata.librarySectionTitle}{C.RESET} 上的"
                     F"媒体 {C.BOLD}{C.Magenta}{payload.Metadata.title}{C.RESET}")

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


class Tag(BaseModel):
    key: str
    value: str


def read_tags():
    with open('func_localization_tags.json', 'r') as file:
        return json.load(file)


def write_tags(tags):
    with open('func_localization_tags.json', 'w') as file:
        json.dump(tags, file, ensure_ascii=False)


@app.get("/api/tags")
def get_tags():
    return read_tags()


@app.post("/api/tags")
def add_tag(tag: Tag):
    tags = read_tags()
    tags[tag.key] = tag.value
    write_tags(tags)
    return {"success": True}


@app.delete("/api/tags")
def delete_tag(tag: Tag):
    tags = read_tags()
    if tag.key in tags:
        del tags[tag.key]
        write_tags(tags)
        return {"success": True}
    else:
        return {"success": False}
