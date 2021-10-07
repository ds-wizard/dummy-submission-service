import fastapi
import fastapi.responses
import os
import pathlib
import uuid

from dummy_submitter.config import cfg_parser
from dummy_submitter.consts import NICE_NAME, VERSION, BUILD_INFO,\
    ENV_CONFIG, DEFAULT_CONFIG
from dummy_submitter.logger import LOG, init_default_logging, init_config_logging

app = fastapi.FastAPI(
    title=NICE_NAME,
    version=VERSION,
)
cfg = cfg_parser.config


def _valid_token(request: fastapi.Request) -> bool:
    if not cfg.security.enabled:
        LOG.debug('Security disabled, authorized directly')
        return True
    auth = request.headers.get('Authorization', '')  # type: str
    if not auth.startswith('Bearer '):
        LOG.debug('Invalid token (missing or without "Bearer " prefix')
        return False
    token = auth.split(' ', maxsplit=1)[1]
    return token in cfg.security.tokens


@app.get(path='/')
async def get_info():
    return fastapi.responses.JSONResponse(
        content=BUILD_INFO,
    )


@app.post(path='/submit')
async def submit(request: fastapi.Request):
    # (1) Verify authorization
    if not _valid_token(request=request):
        return fastapi.responses.PlainTextResponse(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            content='Unauthorized submission request.\n\n'
                    'The submission service is not configured properly.\n'
        )
    # (2) Get data and code
    code = request.headers.get('X-Code', cfg.service.code)
    data = await request.body()
    submission_id = str(uuid.uuid4())
    location = f'https://example.com/submission/{submission_id}'
    # (3) Return response
    if code == 'ok':
        return fastapi.responses.JSONResponse(
            headers={
                'Location': location,
            },
            status_code=fastapi.status.HTTP_201_CREATED,
            content={
                'uuid': submission_id,
                'location': location,
                'length': len(data),
            }
        )
    elif code == 'error':
        return fastapi.responses.PlainTextResponse(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f'Sorry... wild error appeared.\n\n'
                    f'The error prevented the document to be submitted.\n'
                    f'But the document was nice and got {len(data)} bytes.\n'
        )
    return fastapi.responses.PlainTextResponse(
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        content='You sent some BAD REQUEST.\n\n'
                'You are very bad and the service could not figure out'
                'what to do with your weird request.\n'
    )


@app.on_event("startup")
async def app_init():
    global cfg
    init_default_logging()
    config_file = os.getenv(ENV_CONFIG, DEFAULT_CONFIG)
    try:
        with pathlib.Path(config_file).open() as fp:
            cfg = cfg_parser.parse_file(fp=fp)
        init_config_logging(config=cfg)
    except Exception as e:
        LOG.warn(f'Failed to load config: {config_file}')
        LOG.debug(str(e))
    LOG.info(f'Loaded config: {config_file}')
