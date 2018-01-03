
import structlog
from behaviours.default import DefaultBehaviour

class Behaviour():
    def __init__(self, behaviour_config):
        self.behaviour_config = behaviour_config

    def get_behaviour(self, selected_behaviour):
        if selected_behaviour == 'default':
            behaviour = DefaultBehaviour()
        return behaviour
