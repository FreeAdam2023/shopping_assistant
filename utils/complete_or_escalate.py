"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""
"""
@Time ： 2024-11-15
@Auth ： Adam Lyu
"""

from pydantic import BaseModel, Field


class CompleteOrEscalate(BaseModel):
    """
    A utility to mark the current task as completed or to escalate control of the dialog back to the main assistant.
    """

    cancel: bool = Field(
        True,
        description="Whether to cancel the current task. True indicates that the task is canceled.",
    )
    reason: str = Field(
        ...,
        description="The reason for completion or escalation.",
    )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "cancel": True,
                    "reason": "User changed their mind about the current task.",
                },
                {
                    "cancel": True,
                    "reason": "The task has been successfully completed.",
                },
                {
                    "cancel": False,
                    "reason": "I need additional information to proceed.",
                },
            ]
        }
