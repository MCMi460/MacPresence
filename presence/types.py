from enum import Enum


class ActivityType(Enum):
    """
    https://discord.com/developers/docs/developer-tools/game-sdk#activitytype-enum
    "type" must be one of 0, 2, 3, 5 -- Discord only implemented these four
    """

    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


class StatusDisplayType(Enum):
    """
    https://discord.com/developers/docs/events/gateway-events#activity-object-status-display-types
    Default is NAME (0)
    """

    NAME = 0
    STATE = 1
    DETAILS = 2
