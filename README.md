# AI Appointment Scheduling Call Center Demo

A tech demo for scheduling an appointment by speaking with an AI healthcare call center.

## About

This project creates a server instantiating a publicly exposed AI call center to schedule 
doctor appointments. Upon calling the number, the patient will be speaking with 
a conversational AI agent (by default "Rachel") which will:

1. Guide them through sharing relevant healthcare intake info for scheduling
2. Offering example availabilities (time, place, doctor)
3. Confirming appointment based on availability selection
4. Sending text to confirm said appointment

### Stack
* Local Python [FastAPI](https://fastapi.tiangolo.com/) RESTful server with [ngrok](https://ngrok.com/) tunnel for exposing it
* AI vocoding and telephony managed by [vocode.dev](https://www.vocode.dev/), which orchestrates with the following services:
    - Transcribing (caller voice to text) by [Deepgram](https://deepgram.com/)
    - Synthesizing (AI text to voice) by [ElevenLabs](https://elevenlabs.io/)
    - Agent (the AI model itself) by [OpenAI](https://platform.openai.com/)
    - Telephony (in/outbound calling) by [Twilio](https://www.twilio.com/)
* Redis for in-memory storage

### Documentation
While there are already choice links to tech sites and docs throughout this README, the following are some more specific links which I found to be particularly useful.

#### Vocode 
* [Vocode python quickstart](https://docs.vocode.dev/open-source/python-quickstart)
* [Vocode action agents](https://docs.vocode.dev/open-source/action-agents)
* [Streaming examples](https://github.com/vocodedev/vocode-python/tree/main/playground/streaming)
* [Application examples](https://github.com/vocodedev/vocode-python/tree/main/apps)
* [App examples hosted on Replit](https://replit.com/@vocode)
* [Sourcecode for AI agents](https://github.com/vocodedev/vocode-python/tree/main/vocode/streaming/agent)
* [Sourcecode for AI actions](https://github.com/vocodedev/vocode-python/tree/main/vocode/streaming/action)
* [Searching the Vocode-python repo](https://github.com/vocodedev/vocode-python)

#### ngrok
* [Getting started](https://ngrok.com/docs/getting-started/)

#### OpenAI
* [Make API key](https://platform.openai.com/account/api-keys)

#### Twilio
* [Sending SMS message with Python](https://www.twilio.com/docs/sms/quickstart/python)


## Prerequisites & Assumptions
* [Python 3.8+](https://python.org/)
* Audio processing: [ffmpeg](https://ffmpeg.org/)
* Python dep management: [Poetry](https://python-poetry.org/)
* Python virtual environment: [venv](https://docs.python.org/3/library/venv.html)
* Memory: [Redis](https://redis.com/) 
* Server: [ngrok](https://ngrok.com/)
* Containerization (optional): [Docker](https://docker.com)
* API Tokens (See [Installation](#installation) on where to put the details):
    - Deepgram
    - OpenAI
    - ElevenLabs
    - Twilio (must have phone number)

## Project Structure
```bash
.
├── .env.template # Environment template file
├── .gitignore # Which folders and files git will not track
├── README.md # This file
├── callcenter # Source folder for additional Python modules
│   ├── action_factory.py # Factory to handle creating custom actions in subfolder below
│   └── actions # Custom actions for the AI agent (anything we want it to do beyond talking)
│       ├── best_times.py # Return best appointment availabilities to user (info required)
│       └── send_text.py # Final step (info required + appointment accepted) of sending confirmation text
├── config.yaml # Project-specific values (right now only used for constants)
├── docker-compose.yml # Docker configuration
├── Dockerfile # The Docker container "recipe"
├── main.py # The entry point and core logic of the server application
├── poetry.lock # List of the installed versions of Poetry dependencies
├── pyproject.toml # Defines project information and poetry dependencies
└── requirements.txt # Pip-friendly list of dependencies 
```


## Installation & Running
> Based on the very useful [vocode Python docs](https://docs.vocode.dev/open-source/telephony)
> If you find yourself wanting more details check that out.

1. Clone / download this repo and `cd` into it
2. Create environment file out of template then fill with corresponding values with `cp .env.template .env`
3. Set up tunneling with `ngrok http 3000`
- Be sure to [configure ngrok](https://ngrok.com/docs/getting-started/)
- This is crucial for communicating with the outside world and services, _especially_ webhooks
- In `.env` change `BASE_URL` to `<yoururl>.ngrok.app` generated by `ngrok`
- Be sure to [add a webhook to your Twilio number](https://www.twilio.com/docs/usage/webhooks/webhooks-overview) with the url `https://<yoururl>.ngrok.app/inbound_call` to enable
our server defined in `main.py` to handle incoming calls with its `inbound_call` endpoint
4. Open another terminal window, setup a virtual environment: `python3 -m venv env; source env/bin/activate`
5. Install dependencies with `poetry install`
- Make sure you [install Poetry](https://python-poetry.org/docs/)
6. Launch Redis: `brew services start redis`
7. Run the actual server: `poetry run uvicorn main:app --port 3000`
8. Test it out by calling your Twilio number!


## Final Notes

### Tech Eval
#### Pros
* Vocode easily connects with services for transcription, synthesizing, and AI agents
* ActionAgents (used here) are very powerful, a docstring can tell ChatGPT
what action to trigger and what to pass it 
* Actions and Agents are highly customizable
#### Cons
* Open source library nascent, and there's a lack of documentation for especially newer and more rapidly changing features such as actions
* There were some very ad-hoc changes required to get certain custom actions to work, such as needing to modify the `ActionFactory` in original the Python module file itself (dev confirmed this is currently the way to do this)

### Looking Forward
* Using `redis` and kubernetes on cloud deployments not only great for 
data managament but scalability of service
    - SortedSets can make use cases for scheduling faster (e.g. pulling best times)
* For HIPPA compliance and competitive edge, self-managed AI agents can be used instead (See the [list here](https://github.com/vocodedev/vocode-python/tree/main/vocode/streaming/agent))
    - If CICD and resource usage can be optimized, a custom LLM agent such as Llama can be trained and used
* Use of `langchain` could be very powerful to handle autonomous actions such as contacting insurance to validate information (think of the applications beyond scheduling)