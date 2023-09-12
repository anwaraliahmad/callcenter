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
    pass


class TwilioSendTextParameters(BaseModel):
    """Required parameters passed by the agent to the action to send a text.
    Each field (sans phone_number -- the text recipient) is used
    to construct the message itself (an appointment confirmation).
    """
    doctor: str = Field(..., description="The name of the doctor for the appointment.")
    location: str = Field(..., description="The location of the appointment.")
    datetime: str = Field(..., description="The date and time of the appointment.")
    first_name: str = Field(..., description="The first name of the patient.")
    phone_number: str = Field(..., description="The number to send text to (+1XXXXXXXXXX)")


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
        """Send a text message to the patient to confirm the appointment they agreed
        to after they provided all required details.
        


        Returns:
            ActionOutput[TwilioSendTextResponse]: _description_
        """
        # Set up the Twilio API client
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client(account_sid, auth_token)

        # Create appointment confirmation message
        message_body = f'Dear {action_input.params.first_name}: your \
                            appointment with {action_input.params.doctor} at \
                            {action_input.params.location} at {action_input.params.datetime} \
                            has been confirmed. Do not reply.'
        # Send message
        message = client.messages \
                        .create(
                            body=message_body,
                            from_=os.getenv('PHONE_NUMBER'),
                            to=action_input.params.phone_number
                        )
        # Print message for testing purposes
        print(f'Message {message.sid} sent: {message_body}')

        # End action
        return ActionOutput(
            action_type=self.action_config.type,
            response=TwilioSendTextResponse(success=True),
        )
