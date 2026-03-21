from abc import ABC, abstractmethod

class Action(ABC):

    @property
    @abstractmethod
    # name of action (ex: speak)
    def name(self):
        pass


    @property
    @abstractmethod
    # type of values (ex: <text> or <motion: node, shake head, dance>)
    # use formate <type>[: (define type values if needed)]
    def type(self):
        pass


    @property
    @abstractmethod
    # a line to describe robot motion
    # should be present tense
    # ex: robot says:
    # ex: robot moving with:
    def tag(self):
        pass

    @abstractmethod
    # used to execute action
    # arg is arument needed to perform action such as text to speak or movement to perform
    def execute(self, arg):
        pass