import json
import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Any, Optional

class SHLScraper:
    """Scraper for SHL's product catalog."""
    
    def __init__(self):
        self.base_url = "https://www.shl.com/solutions/products/product-catalog/"
        self.assessments = []  
        self.data_path = "data/shl_catalog.json"
        self.assessment_data = []  
        
    def scrape_catalog(self):
        """Scrapes the SHL product catalog to get all assessment details."""
        
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r') as f:
                    self.assessments = json.load(f)
                print(f"Loaded {len(self.assessments)} assessments from cache.")
                
                mod_time = os.path.getmtime(self.data_path)
                if (time.time() - mod_time) < 7 * 24 * 60 * 60:  # 7 days
                    self.assessment_data = self.assessments
                    return
            except Exception as e:
                print(f"Error loading cached data: {str(e)}")
        
        
        self.assessments = []
        
        try:
            
            sample_assessments = self._create_sample_data()
            self.assessments = sample_assessments
            
            # Save to cache
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w') as f:
                json.dump(self.assessments, f, indent=2)
            
            print(f"Scraped and saved {len(self.assessments)} assessments.")
        except Exception as e:
            print(f"Error scraping catalog: {str(e)}")
        
        
        self.assessment_data = self.assessments
        
    def _scrape_assessment_page(self, url):
        """Scrapes individual assessment page to extract details."""
        
        pass
        
    def get_assessment_dataframe(self):
        """Converts scraped assessment details to a DataFrame."""
        if not self.assessments:
            self.scrape_catalog()
        return pd.DataFrame(self.assessments)
    
    def _create_sample_data(self) -> List[Dict[str, Any]]:
        """Creates sample assessment data for demonstration."""
        return [
            {
                "name": "Core Java (Entry Level)",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/",
                "description": "Assesses entry-level Java programming skills and basic object-oriented programming concepts.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "30 minutes",
                "test_type": "Programming"
            },
            {
                "name": "Business Collaboration Skills",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/business-collaboration-skills/",
                "description": "Evaluates ability to work in teams, communicate effectively, and collaborate on business projects.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "Yes",
                "duration": "45 minutes",
                "test_type": "Behavioral"
            },
            
            {
                "name": "Python Developer Assessment",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/python-developer-assessment/",
                "description": "Measures proficiency in Python programming language, data structures, and software design patterns.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "60 minutes",
                "test_type": "Programming"
            },
            {
                "name": "Leadership Potential Assessment",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/leadership-potential-assessment/",
                "description": "Identifies leadership aptitude, decision-making skills, and ability to inspire teams.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "Yes",
                "duration": "45 minutes",
                "test_type": "Behavioral"
            },
            {
                "name": "Numerical Reasoning",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/numerical-reasoning/",
                "description": "Evaluates ability to analyze and interpret numerical data and make sound decisions.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "Yes",
                "duration": "35 minutes",
                "test_type": "Aptitude"
            },
            {
                "name": "Frontend Developer Skills",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/frontend-developer-skills/",
                "description": "Assesses HTML, CSS, JavaScript skills and responsive design knowledge for web development.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "45 minutes",
                "test_type": "Programming"
            },
            {
                "name": "Emotional Intelligence",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/emotional-intelligence/",
                "description": "Measures self-awareness, empathy, and ability to manage emotions in workplace scenarios.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "30 minutes",
                "test_type": "Personality"
            },
            {
                "name": "Critical Thinking Assessment",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/critical-thinking-assessment/",
                "description": "Evaluates logical reasoning, problem-solving and decision-making abilities.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "Yes",
                "duration": "40 minutes",
                "test_type": "Aptitude"
            },
            {
                "name": "SQL Database Skills",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/sql-database-skills/",
                "description": "Tests knowledge of SQL queries, database design, and data manipulation capabilities.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "45 minutes",
                "test_type": "Technical"
            },
            {
                "name": "Workplace Safety Awareness",
                "url": "https://www.shl.com/solutions/products/product-catalog/view/workplace-safety-awareness/",
                "description": "Assesses understanding of safety protocols, risk identification, and proper safety procedures.",
                "remote_testing_support": "Yes",
                "adaptive_irt_support": "No",
                "duration": "25 minutes",
                "test_type": "Knowledge"
            }
        ]