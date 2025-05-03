import matplotlib.pyplot as plt
from typing import List, Dict, Any, Set
import json
import os

from recommendation_engine import RecommendationEngine

# Test data
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
        "query": "Database administrator with SQL expertise",
        "relevant_assessments": [
            "https://www.shl.com/solutions/products/product-catalog/view/sql-database-skills/"
        ]
    }
]

class Evaluator:
    """Evaluates the recommendation engine using standard ranking metrics."""
    
    def __init__(self, engine: RecommendationEngine):
        self.engine = engine
        self.test_data = TEST_QUERIES
    
    def evaluate(self, k_values: List[int] = [3, 5, 10]) -> Dict[str, Dict[int, float]]:
        """Evaluate the recommendation engine on the test dataset."""
        results = {
            "recall": {},
            "map": {}
        }
        
        for k in k_values:
            results["recall"][k] = self._evaluate_recall_at_k(k)
            results["map"][k] = self._evaluate_map_at_k(k)
        
        return results
    
    def _evaluate_recall_at_k(self, k: int) -> float:
        """Calculate Mean Recall@K across all test queries."""
        recalls = []
        
        for test_case in self.test_data:
            query = test_case["query"]
            relevant_urls = set(test_case["relevant_assessments"])
            
            # Get recommendations
            result = self.engine.recommend(query, max_results=k)
            recommendations = result["recommendations"]
            
            # Calculate recall
            retrieved_urls = set(rec["url"] for rec in recommendations[:k])
            if len(relevant_urls) > 0:
                recall = len(retrieved_urls.intersection(relevant_urls)) / len(relevant_urls)
                recalls.append(recall)
        
        # Calculate mean recall
        if recalls:
            return sum(recalls) / len(recalls)
        return 0.0
    
    def _evaluate_map_at_k(self, k: int) -> float:
        """Calculate Mean Average Precision@K across all test queries."""
        aps = []
        
        for test_case in self.test_data:
            query = test_case["query"]
            relevant_urls = set(test_case["relevant_assessments"])
            
            # Get recommendations
            result = self.engine.recommend(query, max_results=k)
            recommendations = result["recommendations"]
            
            # Calculate average precision
            ap = self._calculate_average_precision(recommendations, relevant_urls, k)
            aps.append(ap)
        
        # Calculate mean average precision
        if aps:
            return sum(aps) / len(aps)
        return 0.0
    
    def _calculate_average_precision(self, recommendations: List[Dict[str, Any]], 
                                   relevant_urls: set, k: int) -> float:
        """Calculate Average Precision@K for a single query."""
        hits = 0
        sum_precisions = 0.0
        
        for i, rec in enumerate(recommendations[:k]):
            if rec["url"] in relevant_urls:
                hits += 1
                precision = hits / (i + 1)
                sum_precisions += precision
        
        if hits > 0:
            return sum_precisions / min(len(relevant_urls), k)
        return 0.0
    
    def run_detailed_evaluation(self) -> Dict[str, Any]:
        """Run a detailed evaluation and return comprehensive results."""
        detailed_results = {
            "per_query": [],
            "overall": self.evaluate()
        }
        
        for test_case in self.test_data:
            query = test_case["query"]
            relevant_urls = set(test_case["relevant_assessments"])
            
            # Get recommendations
            result = self.engine.recommend(query, max_results=10)
            recommendations = result["recommendations"]
            
            # Calculate metrics
            retrieved_urls = [rec["url"] for rec in recommendations]
            retrieved_relevant = [url for url in retrieved_urls if url in relevant_urls]
            
            query_result = {
                "query": query,
                "relevant_count": len(relevant_urls),
                "retrieved_relevant_count": len(retrieved_relevant),
                "recall_at_5": len([url for url in retrieved_urls[:5] if url in relevant_urls]) / len(relevant_urls) if relevant_urls else 0,
                "precision_at_5": len([url for url in retrieved_urls[:5] if url in relevant_urls]) / 5 if len(retrieved_urls) >= 5 else 0,
                "recommendations": recommendations
            }
            
            detailed_results["per_query"].append(query_result)
        
        return detailed_results
    
    def plot_results(self, results: Dict[str, Dict[int, float]]):
        """Plot evaluation results."""
        k_values = sorted(results["recall"].keys())
        recall_values = [results["recall"][k] for k in k_values]
        map_values = [results["map"][k] for k in k_values]
        
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(k_values, recall_values, 'o-', label='Recall@K')
        plt.xlabel('K')
        plt.ylabel('Recall')
        plt.title('Recall@K')
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(k_values, map_values, 'o-', label='MAP@K')
        plt.xlabel('K')
        plt.ylabel('MAP')
        plt.title('MAP@K')
        plt.grid(True)
        
        plt.tight_layout()
        
        # Save the plot
        os.makedirs("data", exist_ok=True)
        plt.savefig("data/evaluation_results.png")
        
        return "data/evaluation_results.png"
    
    def print_results(self, results: Dict[str, Dict[int, float]]):
        """Print evaluation results in a formatted way."""
        print("\n--- Evaluation Results ---")
        print("\nRecall@K:")
        for k, value in sorted(results["recall"].items()):
            print(f"  Recall@{k}: {value:.4f}")
        
        print("\nMean Average Precision@K:")
        for k, value in sorted(results["map"].items()):
            print(f"  MAP@{k}: {value:.4f}")