from pydantic import BaseModel, Field
from .enums import ProcessingStatus, AnswerMethod


# --- Internal data models ---

class ActSection(BaseModel):
    act: str
    section: str | None
    title: str
    text: str


class QAPair(BaseModel):
    source: str
    question: str
    answer: str


# --- Request models ---

class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    language: str = Field(default="en", pattern="^(en|hi)$")


# --- Response models ---

class FileMetadata(BaseModel):
    page_count: int = 0
    confidence_score: float = 0.0


class FileUploadResult(BaseModel):
    file_id: str
    status: ProcessingStatus
    raw_text: str = ""
    metadata: FileMetadata = Field(default_factory=FileMetadata)
    error: str | None = None


class BatchUploadResponse(BaseModel):
    batch_id: str
    results: list[FileUploadResult]


class AskResponse(BaseModel):
    answer: str
    source: str
    method: AnswerMethod
    confidence: float | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    llm_mode: str


# --- Document Summary models ---

class SummaryRequest(BaseModel):
    document_text: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="en", pattern="^(en|hi)$")
    detail_level: str = Field(default="standard", pattern="^(brief|standard|detailed)$")


class SummaryResponse(BaseModel):
    summary: str
    key_points: list[str]
    word_count: int
    status: str


# --- Timeline Generator models ---


class TimelineEntry(BaseModel):
    date: str
    event: str

class TimelineRequest(BaseModel):
    document_text: str = Field(..., min_length=1, max_length=50000)
    language: str = Field(default="en", pattern="^(en|hi)$")


class TimelineResponse(BaseModel):
    timeline: list[TimelineEntry]
    event_count: int
    status: str


# --- Voice Assistant models ---

class VoiceQueryRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=5000)
    language: str = Field(default="en", pattern="^(en|hi)$")


class VoiceQueryResponse(BaseModel):
    answer: str
    source: str
    method: str
    confidence: float | None = None
    transcript: str


# --- Judgement Prediction models ---

class JudgementRequest(BaseModel):
    case_description: str = Field(..., min_length=1, max_length=50000)
    case_type: str = Field(default="general", max_length=100)
    language: str = Field(default="en", pattern="^(en|hi)$")


class JudgementResponse(BaseModel):
    prediction: str
    relevant_sections: list[str]
    confidence_level: str
    disclaimer: str
    status: str
