from abc import ABC, abstractmethod
from action_abstract import Action

class DummySpeak(Action):
    @property
    def name(self):
        return "speak"
    
    @property 
    def type(self):
        return "<text>"
    
    @property 
    def tag(self):
        return "Robot says: "
    
    def execute(self, arg):

        # use reachy bot api to create sound

        return True