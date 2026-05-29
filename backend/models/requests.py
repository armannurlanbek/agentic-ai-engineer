from typing import Optional

from pydantic import BaseModel, Field

from backend.models.enums import ContentType


class GenerateRequest(BaseModel):
    topic: str
    content_type: ContentType = ContentType.TWEET
    urls: list[str] = Field(default_factory=list)
    voice_description: str = ""
    target_length: str = "medium"
    original_tweet_text: str = ""
    user_id: str = "default"
    max_draft_iterations: int = Field(default=3, ge=1, le=5)


class UploadRequest(BaseModel):
    user_id: str
    description: str = ""
