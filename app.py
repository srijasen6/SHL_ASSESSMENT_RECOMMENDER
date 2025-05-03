import streamlit as st
import pandas as pd
import time
import subprocess
import threading
import os
from typing import List, Dict, Any, Optional

from recommendation_engine import RecommendationEngine
from evaluation import Evaluator
from utils import extract_text_from_url, validate_url

# Global variables
engine = RecommendationEngine()
engine.initialize(force_rebuild=True)

# Start API in the background
def run_api():
    try:
        import api
        print("Starting API server...")
        subprocess.Popen(["uvicorn", "api:app", "--host", "localhost", "--port", "8000"])
    except Exception as e:
        print(f"Error starting API: {str(e)}")

# Start API thread
api_thread = threading.Thread(target=run_api)
api_thread.daemon = True
api_thread.start()

# Set page config
st.set_page_config(
    page_title="SHL Assessment Recommender", 
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("SHL Assessment Recommendation System")
st.markdown("""
This tool helps you find the most relevant SHL assessments based on your job description or requirements.
Simply enter a job description or specific skills you're looking for, and we'll recommend the best SHL assessments.
""")

# Create tabs
tab1, tab2 = st.tabs(["Recommendations", "Evaluation"])

# Recommendations tab
with tab1:
    st.header("Find Relevant Assessments")
    
    # Input methods
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            # Input methods
            input_method = st.radio(
                "Choose input method:",
                ["Text query", "Job description URL"],
                horizontal=True
            )
        
        # Query input
        if input_method == "Text query":
            user_query = st.text_area(
                "Enter your query or job description:",
                height=150,
                placeholder="Example: I am hiring for Java developers who need to collaborate with business teams"
            )
            url_input = None
        else:
            url_input = st.text_input(
                "Enter job posting URL:",
                placeholder="https://example.com/job-posting"
            )
            user_query = None
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        search_button = st.button("Find Assessments", type="primary")
    
    with col2:
        max_results = st.selectbox("Max results:", [3, 5, 10], index=1)
    
    # Process search
    if search_button:
        with st.spinner("Finding the best assessments..."):
            # Process URL if provided
            if input_method == "Job description URL" and url_input:
                if not validate_url(url_input):
                    st.error("Invalid URL format. Please enter a valid URL.")
                else:
                    extracted_text = extract_text_from_url(url_input)
                    if not extracted_text:
                        st.error("Could not extract text from the URL. Please try a different URL or use text input.")
                    else:
                        user_query = extracted_text
                        st.info(f"Successfully extracted job description from URL ({len(user_query)} characters)")
            
            # Get recommendations
            if user_query:
                if not engine.initialized:
                    engine.initialize(force_rebuild=True)
                result = engine.recommend(user_query, max_results=max_results)
                recommendations = result["recommendations"]
            else:
                recommendations = []
            
            if recommendations:
                st.subheader(f"Found {len(recommendations)} relevant assessments")
                st.caption(f"Processing time: {result['processing_time']:.2f} seconds")
                
                # Display recommendations
                for i, rec in enumerate(recommendations):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {i+1}. {rec['name']}")
                            st.markdown(f"**Test Type:** {rec['test_type']} | **Duration:** {rec['duration']}")
                            st.markdown(f"**Remote Testing:** {rec['remote_testing_support']} | **Adaptive IRT:** {rec['adaptive_irt_support']}")
                            st.markdown(f"**Relevance Score:** {rec['similarity_score']:.2f}")
                            st.markdown(f"**URL:** [View Assessment]({rec['url']})")
                            
                            if 'description' in rec:
                                with st.expander("Description"):
                                    st.write(rec['description'])
                        
                        st.divider()
            else:
                st.warning("No relevant assessments found. Try refining your query.")

# Evaluation tab
with tab2:
    st.header("System Evaluation")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Evaluation Options")
        eval_button = st.button("Run Evaluation")
        force_rebuild = st.checkbox("Force index rebuild")
    
    # Run evaluation
    if eval_button:
        with st.spinner("Evaluating recommendation quality..."):
            if force_rebuild:
                engine.initialize(force_rebuild=True)
            
            evaluator = Evaluator(engine)
            results = evaluator.evaluate()
            detailed_results = evaluator.run_detailed_evaluation()
            
            # Plot results
            plot_path = evaluator.plot_results(results)
            
            # Display results
            st.subheader("Evaluation Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Recall@K")
                for k, value in sorted(results["recall"].items()):
                    st.metric(f"Recall@{k}", f"{value:.4f}")
            
            with col2:
                st.markdown("### Mean Average Precision@K")
                for k, value in sorted(results["map"].items()):
                    st.metric(f"MAP@{k}", f"{value:.4f}")
            
            # Display plot
            if os.path.exists(plot_path):
                st.image(plot_path)
            
            # Display per-query results
            st.subheader("Per-Query Performance")
            
            for i, query_result in enumerate(detailed_results["per_query"]):
                with st.expander(f"Query {i+1}: {query_result['query']}"):
                    st.markdown(f"**Relevant assessments:** {query_result['relevant_count']}")
                    st.markdown(f"**Retrieved relevant:** {query_result['retrieved_relevant_count']}")
                    st.markdown(f"**Recall@5:** {query_result['recall_at_5']:.4f}")
                    st.markdown(f"**Precision@5:** {query_result['precision_at_5']:.4f}")
                    
                    st.markdown("### Top 5 Recommendations")
                    for j, rec in enumerate(query_result['recommendations'][:5]):
                        st.markdown(f"{j+1}. **{rec['name']}** - Score: {rec['similarity_score']:.4f}")
                        
            st.success("Evaluation completed successfully!")

# Footer
st.markdown("---")
st.caption("SHL Assessment Recommendation System | Built with Streamlit")