from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
import time

from recommendation_engine import RecommendationEngine
from utils import validate_url, extract_text_from_url

# Create global engine instance
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
        _engine.initialize()
    return _engine

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str = Field(..., example="ok")
    version: str = Field(..., example="1.0.0")
    timestamp: int = Field(..., example=1619712000)

class AssessmentResponse(BaseModel):
    assessment_name: str = Field(..., example="Core Java (Entry Level)")
    assessment_url: str = Field(..., example="https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/")
    remote_testing_support: str = Field(..., example="Yes")
    adaptive_irt_support: str = Field(..., example="No")
    duration: str = Field(..., example="30 minutes")
    test_type: str = Field(..., example="Programming")
    similarity_score: float = Field(..., ge=0, le=1, example=0.89)

class RecommendationResponse(BaseModel):
    query: str = Field(..., example="Java developers with business collaboration skills")
    recommendations: List[AssessmentResponse] = Field(..., example=[
        {
            "assessment_name": "Core Java (Entry Level)",
            "assessment_url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/",
            "remote_testing_support": "Yes",
            "adaptive_irt_support": "No",
            "duration": "30 minutes",
            "test_type": "Programming",
            "similarity_score": 0.89
        }
    ])
    count: int = Field(..., example=1)
    processing_time: float = Field(..., example=0.5)

# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="API for recommending SHL assessments based on job descriptions",
    version="1.0.0"
)

# Initialize engine on startup
@app.on_event("startup")
async def startup_event():
    get_engine()
    print("API server running on http://localhost:8000")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": int(time.time())
    }

@app.get("/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
def recommend(
    query: Optional[str] = Query(None, description="Natural language query or job description"),
    url: Optional[str] = Query(None, description="URL to a job description"),
    max_results: int = Query(10, ge=1, le=10, description="Maximum number of results to return")
):
    """
    Recommend SHL assessments based on query or job description URL.
    
    Args:
        query: Natural language query or job description
        url: URL to a job description
        max_results: Maximum number of results to return
        
    Returns:
        Recommendations
    """
    # Input validation
    if not query and not url:
        raise HTTPException(status_code=400, detail="Either query or url parameter is required")
    
    # If URL is provided, extract text
    if url:
        if not validate_url(url):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        text = extract_text_from_url(url)
        if not text:
            raise HTTPException(status_code=404, detail="Could not extract text from URL")
        
        query = text
    
    # Get recommendations
    engine = get_engine()
    result = engine.recommend(query, max_results=max_results)
    
    # Format for API response
    formatted_recs = engine.format_recommendations_for_api(result["recommendations"])
    
    return {
        "query": result["query"],
        "recommendations": formatted_recs,
        "count": len(formatted_recs),
        "processing_time": result["processing_time"]
    }