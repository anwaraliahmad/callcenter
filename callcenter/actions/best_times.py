from pydantic import BaseModel
import typing
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.models.actions import (
    ActionConfig,
    ActionInput,
    ActionOutput
)

# Very ad hoc spoofed availability data
# TODO: Integrate Redis SortedSets containing hashed
# time slot, doctor, and location info (that
# is the best way to do this at scale anyways)
times = {
    'john smith': {
        'time': '2024-03-08 12:00:00.000000',
        'location': '55 Fruit St, Boston, MA 02114'
    },
    'bobby_bobster': {
        'time': '2024-03-08 12:00:00.000000',
        'location': '55 Fruit St, Boston, MA 02114'
    }
}

class BestTimesActionConfig(ActionConfig, type='best_times'):  # type: ignore
    nearest: bool


class BestTimesActionParameters(BaseModel):
    input_str: str



class BestTimesActionResponse(BaseModel):
    success: bool
    message: str


class BestTimesAction(
    BaseAction[BestTimesActionConfig, BestTimesActionParameters, BestTimesActionResponse]
):
    parameters_type: typing.Type[BestTimesActionParameters] = BestTimesActionParameters
    response_type: typing.Type[BestTimesActionResponse] = BestTimesActionResponse

    async def run(
        self, action_input: ActionInput[BestTimesActionParameters]
    ) -> ActionOutput[BestTimesActionResponse]:
        """Retrieves best available appointment times for the patient after they provide 
        their relevant information. This will only be called when all relevant patient info is received.

        The input to this action is a pipe separated list of the following values once you have them from the patient calling:
        - Patient first name 
        - Patient address
        - Patient chief medical reason
        - Patient referral (optional; if provided will be doctor name "<first name> <last_name>" all lowercased)
        Even if there's no referral, include the pipe separating as if it were there.

        The output will be a string with at least one appointment time, 
        each separated by a pipe and in the format of  "<Doctor Name>, <Datetime string>, <Address> | 
        Doctor Name>, <Datetime string>, <Address> " representing each availability details. 

        Be sure to ask and confirm which availability is best (the doctor, time, address) before asking for consent
        to send a confirmation text with these details to a number the patient provides

        example input: John Smith|415 Mission St 3rd Floor, United States|headache||
        """
        print(
            f"Confirm receive {action_input.params.input_str}"
        )
        tentative_appt_arr = f"John Smith,{times['john smith']['time']},{times['john smith']['location']}|Bobby Bobster,{times['bobby_bobster']['time']}, {times['bobby_bobster']['location']}"


        return ActionOutput(
            action_type=self.action_config.type,
            response=BestTimesActionResponse(success=True, message=tentative_appt_arr),
        )
