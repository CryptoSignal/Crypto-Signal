
import structlog
from behaviours.default import DefaultBehaviour
from behaviours.simple_bot import SimpleBot

class Behaviour():
    def __init__(self, behaviour_config):
        self.behaviour_config = behaviour_config

    def get_behaviour(self, selected_behaviour):
        if selected_behaviour == 'default':
            behaviour = DefaultBehaviour(self.behaviour_config[selected_behaviour])
        if selected_behaviour == 'simple_bot':
            behaviour = SimpleBot(self.behaviour_config[selected_behaviour])
            
        return behaviour
