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
        """Retrieves available appointment times for the patient after they provide 
        their relevant information.
        The input to this action is a comma separated list of the following values once you have them from the patient calling:
        - Patient first name 
        - Patient address
        - Patient chief medical reason
        - Patient referral (optional; if provided will be doctor name "<first name> <last_name>" all lowercased)

        The output will a string in the format of "<Doctor Name>, <Datetime string>, <Address>" representing 
        the best appointment time, the AI will proceed to ask the user to confirm this appointment and if so then 
        consent to receiving a confirmation text about it.

        Note: Appointments must be read in a format which is patient friendly. Keep in mind this conversation
        is all voice synthesized to the calling patient.
        """
        print(
            f"Confirm receive {action_input.params.input_str}"
        )
        tentative_appt_arr = f"John Smith, {times['john smith']['time']}, {times['john smith']['location']}"


        return ActionOutput(
            action_type=self.action_config.type,
            response=BestTimesActionResponse(success=True, message=tentative_appt_arr),
        )
