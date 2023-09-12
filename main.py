# if running from python, this will load the local .env
# docker-compose will load the .env file by itself
from dotenv import load_dotenv
load_dotenv()
import yaml
import logging
import os
import sys
from fastapi import FastAPI
from vocode.streaming.models.telephony import TwilioConfig
from pyngrok import ngrok
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import (
    TwilioInboundCallConfig,
    TelephonyServer,
)
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig, TimeEndpointingConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig

from callcenter.action_factory import (
    SchedulingActionFactory
)

from callcenter.actions.best_times import (
    BestTimesAction,
    BestTimesActionConfig
)

from callcenter.actions.send_text import (
    TwilioSendTextAction,
    TwilioSendTextActionConfig
)

# Check development environment
deployment_env = os.getenv('DEPLOYMENT_ENV', 'local')

# Load the YAML config file
config = yaml.load(open('config.yaml',encoding='utf-8'), Loader=yaml.FullLoader)

# Initialize API server
app = FastAPI(docs_url=None)

# Setup logger
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_manager = RedisConfigManager()

# Server base url
BASE_URL = os.getenv("BASE_URL")

# Link base url with the public ngrok tunnel
if not BASE_URL:
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000

    # Open a ngrok tunnel to the dev server
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info('ngrok tunnel "{}" -> "http://127.0.0.1:{}"'.format(BASE_URL, port))

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

# Telephony operations handler
telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            # Define incoming call endpoint
            url="/inbound_call",
            # Configure the AI agent as an OpenAI GPT-3.5-turbo instance
            agent_config=ChatGPTAgentConfig(
                api_key=os.getenv("OPENAI_API_KEY"),
                initial_message=BaseMessage(text=config['open_ai']['first_message']),
                # Preamble to prompt engineer the character / behavior of AI before chatting
                prompt_preamble=config['open_ai']['preamble'],
                # Does it talk?
                generate_responses=True,
                # Pass in custom actions that will contextually trigger 
                # (e.g. get appointment times, send text message)
                action_factory = SchedulingActionFactory(),
                actions=[
                    BestTimesActionConfig(nearest=False),
                    TwilioSendTextActionConfig(send_text=True)
                ]
            ),
            # Configure service for transcribing what caller says (uses Deepgram)
            # `from_telephone_input_device` adjusts parameters to optmize for phone calls
            transcriber_config=DeepgramTranscriberConfig.from_telephone_input_device(
                # endpointing_config sets the method of how the transcriber
                # determines the user is "done" talking at the moment.
                # For now, it's based on a pause after talking
                endpointing_config=TimeEndpointingConfig(),
                api_key=os.getenv("DEEPGRAM_API_KEY")
            ),
            # Configure service for voice synthesizing what the AI outputs (ElevenLabs)
            # `from_telephone_output_device` adjusts parameters to optmize for phone calls
            synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
                api_key=os.getenv("ELEVEN_LABS_API_KEY"),
                voice_id=os.getenv("ELEVEN_LABS_VOICE_ID")
            ),
            # Configure telephony service (Twilio)
            twilio_config=TwilioConfig(
                account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
                auth_token=os.getenv("TWILIO_AUTH_TOKEN")
            ),
        )
    ],
    # Log server operations
    logger=logger
)

# Expose the telephony endpoint(s) to the server
app.include_router(telephony_server.get_router())
