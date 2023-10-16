import os
import cgi
import json
from io import BytesIO
from fastapi import FastAPI, Request
from payload import Payload
import func_localization
from log import log
from log import Color as C

env = os.environ


class Environ:
    LOCALIZATION = bool(env.get('LOCALIZATION', True))
    PLEX_HOST = env.get('PLEX_HOST', 'host.docker.internal')
    PLEX_PORT = env.get('PLEX_PORT', '32400')
    PLEX_TOKEN = env.get('PLEX_TOKEN', '')
    PLEX_URL = f'http://{PLEX_HOST}:{PLEX_PORT}'


app = FastAPI()


@app.post("/")
async def main(request: Request):
    body = await request.body()
    content_type = cgi.parse_header(request.headers.get('content-type'))[1]
    multipart_data = cgi.parse_multipart(
        fp=BytesIO(body),
        pdict={'boundary': bytes(content_type['boundary'], "utf-8")}
    )
    payload = Payload(json.loads(multipart_data.get('payload', "{}")[0]))
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
                func_localization.PlexServer(Environ.PLEX_URL, Environ.PLEX_TOKEN).operate_item(
                    payload.Metadata.ratingKey)

    return 'succes'
