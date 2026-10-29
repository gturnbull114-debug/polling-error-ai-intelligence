"""Agent definitions for AI Polling Intelligence system."""

__all__ = [
    "NormalizerAgent",
    "ModelerAgent",
    "ExplainerAgent",
    "PollBot",
    "POLLBOT_SYSTEM_PROMPT",
    "StatBot",
    "STATBOT_SYSTEM_PROMPT",
    "PollingIntelligenceCollaborator",
    "SequentialPipelineCoordinator",
]


def __getattr__(name: str):
    if name in ("PollBot", "POLLBOT_SYSTEM_PROMPT"):
        from src.agents.pollbot import PollBot, POLLBOT_SYSTEM_PROMPT
        return PollBot if name == "PollBot" else POLLBOT_SYSTEM_PROMPT
    elif name in ("StatBot", "STATBOT_SYSTEM_PROMPT"):
        from src.agents.statbot import StatBot, STATBOT_SYSTEM_PROMPT
        return StatBot if name == "StatBot" else STATBOT_SYSTEM_PROMPT
    elif name in ("PollingIntelligenceCollaborator", "SequentialPipelineCoordinator"):
        from src.agents.collaborator import PollingIntelligenceCollaborator, SequentialPipelineCoordinator
        return PollingIntelligenceCollaborator if name == "PollingIntelligenceCollaborator" else SequentialPipelineCoordinator
    elif name == "NormalizerAgent":
        from src.agents.normalizer import NormalizerAgent
        return NormalizerAgent
    elif name == "ModelerAgent":
        from src.agents.modeler import ModelerAgent
        return ModelerAgent
    elif name == "ExplainerAgent":
        from src.agents.explainer import ExplainerAgent
        return ExplainerAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
