import logging
from vocode.streaming.action.base_action import BaseAction
from vocode.streaming.action.factory import ActionFactory
from vocode.streaming.action.worker import ActionsWorker
from callcenter.actions.best_times import(
    BestTimesAction,
    BestTimesActionConfig
)
from callcenter.actions.send_text import (
    TwilioSendTextAction,
    TwilioSendTextActionConfig
)
from vocode.streaming.models.actions import (
    ActionConfig
)



class SchedulingActionFactory:
    """Overrode factory to handle creation of custom actions by AI agent.
    
    NOTE: As of 09/11/2023, per a developer on the Discord forum for vocode,
    to make this feature work the actual default ActionFactory code itself 
    needs to change to add the custom ActionConfig's as shown below.
    
    e.g. using venv its most likely at
    /path/to/environment_folder/lib/python3.11/site-packages/vocode/streaming/action/factory.py
    """
    def create_action(self, action_config: ActionConfig) -> BaseAction:
        if isinstance(action_config, BestTimesActionConfig):
            return BestTimesAction(action_config, should_respond=True)
        elif isinstance(action_config, TwilioSendTextActionConfig):
            return TwilioSendTextAction(action_config, should_respond=True)
        else:
            raise Exception("Invalid action type")