from typing import Optional, Type
from pydantic import BaseModel, Field
import os
from twilio.rest import Client
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput,
    ActionType,
)


class TwilioSendTextActionConfig(ActionConfig, type='send_text'):
    """Configuration for TwilioSendTextAction. Used by the agent 
    and action factory to create the TwilioSendTextAction.
    """
    send_text: bool
    pass


class TwilioSendTextParameters(BaseModel):
    input_str: str
    

class TwilioSendTextResponse(BaseModel):
    """The return object after the TwilioSendTextAction is triggered and ran.

    success -- set to True if action succeeded
    """
    success: bool


class TwilioSendTextAction(
    BaseAction[
        TwilioSendTextActionConfig, TwilioSendTextParameters, TwilioSendTextResponse
    ]
):
    parameters_type: Type[TwilioSendTextParameters] = TwilioSendTextParameters
    response_type: Type[TwilioSendTextResponse] = TwilioSendTextResponse

    async def run(
        self, action_input: ActionInput[TwilioSendTextParameters]
    ) -> ActionOutput[TwilioSendTextResponse]:
        """Sends a text message with appointment details to the patient's phone number
        once they provided all required information and confirmed an available time.

        The patient must select an appointment (doctor, location, time) from availabilities
        (get best times) before this action
        is triggered. 

        The input to this action is a pipe separated list of the patient name, patient phone number (digits only), 
        name of doctor for appointment, address of appointment, time of appointment 
        e.g. John Smith|8888888888|Bobby Jones|55 Fruit St, Boston, MA 02114|2024-03-08 12:00:00.000000
        """
        # Set up the Twilio API client
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)
        print(f'Text message params {action_input.params.input_str}')

        first_name, phone_number, doctor, location, datetime = action_input.params.input_str.split('|')


        # Create appointment confirmation message
        message_body = f'Dear {first_name}, your\
                            appointment with {doctor} at\n\
                            {location} on {datetime}\
                            has been confirmed. Do not reply.'
        # Send message
        message = client.messages \
                        .create(
                            body=message_body,
                            from_=os.getenv('PHONE_NUMBER'),
                            to=f"+1{phone_number}"
                        )
        # Print message for testing purposes
        print(f'Message {message.sid} sent: {message_body}')

        # End action
        return ActionOutput(
            action_type=self.action_config.type,
            response=TwilioSendTextResponse(success=True),
        )
