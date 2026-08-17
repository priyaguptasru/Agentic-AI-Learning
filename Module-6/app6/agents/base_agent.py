from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Base class for all specialized agents.

    Every agent has:
    - name
    - description
    - version
    - execute() interface
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        version: str = "1.0",
    ):

        self.name = name
        self.description = description
        self.version = version

    @abstractmethod
    def execute(self, task):
        """
        Execute the assigned task.

        Every specialized agent must implement
        this method.
        """
        raise NotImplementedError

    def info(self):
        """
        Return agent metadata.
        """

        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
        }
