from pydantic import BaseModel, Field
from typing import Optional


class UserProfile(BaseModel):
    name: str
    age: int = Field(ge=18, le=100)
    annual_income: float = Field(ge=0)
    monthly_expenses: float = Field(ge=0)
    current_savings: float = Field(ge=0)
    current_investments: float = Field(default=0.0, ge=0)
    debt: float = Field(default=0.0, ge=0)
    risk_tolerance: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$")
    financial_goals: list[str] = Field(default_factory=list)
    investment_preferences: list[str] = Field(default_factory=list)
    time_horizon_years: int = Field(default=10, ge=1, le=50)
    epf_monthly: float = Field(default=0.0, ge=0)
    hra_monthly: float = Field(default=0.0, ge=0)
    rent_monthly: float = Field(default=0.0, ge=0)
    metro_city: bool = Field(default=True)


class AdvisorRequest(BaseModel):
    profile: UserProfile
    question: Optional[str] = None


class AdvisorResponse(BaseModel):
    category: str
    advice: str
    profile_summary: str


class AgentChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    profile: Optional[UserProfile] = None
