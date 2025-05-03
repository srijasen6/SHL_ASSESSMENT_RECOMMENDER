import time
import re
from typing import List, Dict, Any, Optional
import numpy as np

from scraper import SHLScraper
from indexer import AssessmentIndexer
from utils import extract_text_from_url, parse_time_constraint

class RecommendationEngine:
    """Recommendation engine for SHL assessments."""
    
    def __init__(self):
        self.scraper = SHLScraper()
        self.indexer = AssessmentIndexer()
        self.initialized = False
    
    def initialize(self, force_rebuild: bool = False):
        """Initialize the recommendation engine by scraping data and creating the index."""
        if self.initialized and not force_rebuild:
            return
        
        # Scrape or load assessment data
        self.scraper.scrape_catalog()
        assessments = self.scraper.assessment_data

        # Create the search index
        self.indexer.create_index(assessments, force_rebuild=force_rebuild)
        
        self.initialized = True
    
    def extract_constraints(self, query: str) -> Dict[str, Any]:
        """Extract constraints from the query like time limits, skills, etc."""
        constraints = {}
        
        # Extract time constraints
        max_duration = parse_time_constraint(query)
        if max_duration:
            constraints["max_duration"] = max_duration
        
        # Extract test type preferences
        test_types = []
        type_keywords = {
            "programming": ["coding", "programming", "developer", "software engineer"],
            "aptitude": ["aptitude", "numerical", "logical", "reasoning"],
            "personality": ["personality", "behavioral", "behaviour", "character"],
            "technical": ["technical", "technology", "IT", "computer"]
        }
        
        for test_type, keywords in type_keywords.items():
            if any(keyword in query.lower() for keyword in keywords):
                test_types.append(test_type.capitalize())
        
        if test_types:
            constraints["test_types"] = test_types
        
        # Extract remote testing requirement
        remote_keywords = ["remote", "online", "virtual", "from home"]
        if any(keyword in query.lower() for keyword in remote_keywords):
            constraints["remote_testing"] = True
        
        return constraints
    
    def enrich_query(self, query: str) -> str:
        """Enrich the query to make it more effective for retrieval."""
        # Add synonyms for common terms
        enriched_query = query
        
        # For Java developer collaboration searches
        if "java" in query.lower() and ("collaborate" in query.lower() or "business" in query.lower()):
            enriched_query += " Core Java Entry Level Business Collaboration Skills team communication cooperation"
        
        # Other synonym mappings...
        synonym_mappings = {
            r'\bdev\b': 'developer',
            r'\bcoder\b': 'programmer',
            r'\bcoding\b': 'programming',
            r'\bremote\b': 'online virtual',
            r'\bmanager\b': 'leadership management',
            r'\bleader\b': 'leadership management',
            r'\bjava\b': 'programming developer coding Core Entry Level',
            r'\bteams\b': 'collaboration teamwork communication'
        }
        
        for pattern, replacement in synonym_mappings.items():
            if re.search(pattern, query.lower()):
                enriched_query += f" {replacement}"
        
        # Add context terms based on domain-specific words
        domain_mappings = {
            r'front.?end': 'HTML CSS JavaScript UI',
            r'back.?end': 'server API database',
            r'full.?stack': 'frontend backend database',
            r'data\s*scien': 'statistics analytics machine learning',
            r'secur': 'OWASP cybersecurity encryption'
        }
        
        for pattern, context in domain_mappings.items():
            if re.search(pattern, query.lower()):
                enriched_query += f" {context}"
        
        return enriched_query
    
    def recommend(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Recommend assessments based on the query."""
        start_time = time.time()
        
        # Make sure engine is initialized
        if not self.initialized:
            self.initialize(force_rebuild=True)
            
        # Check if query is a URL
        if query.startswith('http'):
            url_content = extract_text_from_url(query)
            if url_content:
                query = url_content
        
        # Extract constraints
        constraints = self.extract_constraints(query)
        
        # Enrich query
        enriched_query = self.enrich_query(query)
        
        # Search for matching assessments
        results = self.indexer.search(enriched_query, top_k=max(max_results * 2, 20))
        
        # Apply filters from constraints
        if constraints:
            results = self.indexer.filter_results(
                results,
                max_duration=constraints.get("max_duration"),
                test_types=constraints.get("test_types"),
                remote_testing=constraints.get("remote_testing")
            )
        
        # Limit results
        results = results[:max_results]
        
        # Add processing time
        processing_time = time.time() - start_time
        result_package = {
            "query": query,
            "recommendations": results,
            "count": len(results),
            "processing_time": processing_time
        }
        
        return result_package
    
    def format_recommendations_for_api(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations for API response."""
        formatted_recs = []
        for rec in recommendations:
            formatted_rec = {
                "assessment_name": rec.get("name", ""),
                "assessment_url": rec.get("url", ""),
                "remote_testing_support": rec.get("remote_testing_support", "Unknown"),
                "adaptive_irt_support": rec.get("adaptive_irt_support", "Unknown"),
                "duration": rec.get("duration", "Unknown"),
                "test_type": rec.get("test_type", "Unknown"),
                "similarity_score": rec.get("similarity_score", 0.0)
            }
            formatted_recs.append(formatted_rec)
        return formatted_recs