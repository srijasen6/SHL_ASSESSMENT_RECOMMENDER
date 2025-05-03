"""
Test dataset for evaluating the SHL Assessment Recommendation system.
This data is extracted from sample job descriptions.
"""

# Test queries with relevant assessments
TEST_QUERIES = [
    {
        "query": "Java developers with business collaboration skills",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/core-java-entry-level-new/",
            "https://www.shl.com/solutions/products/product-catalog/view/business-collaboration-skills/"
        ]
    },
    {
        "query": "Frontend developer with UI/UX experience",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/frontend-developer-skills/"
        ]
    },
    {
        "query": "Python data scientist with good communication",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/python-developer-assessment/",
            "https://www.shl.com/solutions/products/product-catalog/view/business-collaboration-skills/"
        ]
    },
    {
        "query": "Team leader with good decision making skills",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/leadership-potential-assessment/",
            "https://www.shl.com/solutions/products/product-catalog/view/critical-thinking-assessment/"
        ]
    },
    {
        "query": "Data analyst with SQL skills",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/sql-database-skills/",
            "https://www.shl.com/solutions/products/product-catalog/view/numerical-reasoning/"
        ]
    }
]

# Function to get test data
def get_test_data():
    return TEST_QUERIES