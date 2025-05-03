import os
import re
import json
import string
import numpy as np
import faiss
from typing import List, Dict, Any, Optional

class AssessmentIndexer:
    """Creates and manages vector embeddings for SHL assessments."""
    
    def __init__(self):
        self.data_dir = "data"
        self.index_path = os.path.join(self.data_dir, "assessment_index.faiss")
        self.vocab_path = os.path.join(self.data_dir, "vocabulary.json")
        self.vocabulary = {}
        self.vector_size = 300  # Dimension of vectors
        self.assessment_data = []
        self.index = None
    
    def create_index(self, assessments: List[Dict[str, Any]], force_rebuild: bool = False):
        """Creates a vector index from the assessment data."""
        self.assessment_data = assessments
        
        # Create data dir if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Check if index already exists
        if not force_rebuild and os.path.exists(self.index_path) and os.path.exists(self.vocab_path):
            try:
                # Load vocabulary
                with open(self.vocab_path, 'r') as f:
                    self.vocabulary = json.load(f)
                
                # Load index
                self.index = faiss.read_index(self.index_path)
                print(f"Loaded index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                print(f"Error loading cached index: {str(e)}")
                print("Rebuilding index...")
        
        print("Creating new assessment embeddings...")
        
        # Prepare text data for embedding
        texts = []
        for assessment in assessments:
            # Combine name and description for better representation
            text = f"{assessment['name']} {assessment['description']} {assessment['test_type']}"
            texts.append(text)
        
        # Build vocabulary from texts
        self._build_vocabulary(texts)
        
        # Create embeddings
        embeddings = self._create_embeddings(texts)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.vector_size)  # Inner product similarity
        self.index.add(embeddings)
        
        # Save index and vocabulary
        faiss.write_index(self.index, self.index_path)
        with open(self.vocab_path, 'w') as f:
            json.dump(self.vocabulary, f)
        
        print(f"Created index with {self.index.ntotal} vectors of dimension {self.vector_size}")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Searches for assessments that match the query."""
        if not self.index or not self.assessment_data:
            raise ValueError("Index not created. Call create_index first.")
        
        # Print for debugging
        print(f"Searching for: {query}")
        print(f"Index has {self.index.ntotal} vectors")
        print(f"Vocabulary size: {len(self.vocabulary)}")
        
        
        query_vector = self._embed_query(query)
        
        # Search index
        distances, indices = self.index.search(query_vector, top_k)
        
        
        print(f"Top distances: {distances[0]}")
        print(f"Top indices: {indices[0]}")
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(self.assessment_data):  # Valid index
                result = self.assessment_data[idx].copy()
                # Convert similarity from distance
                similarity = float(distances[0][i])
                result["similarity_score"] = max(0.0, min(1.0, similarity))
                results.append(result)
        
        
        results = [r for r in results if r.get("similarity_score", 0) > 0.1]  # Lower threshold from 0.5 to 0.1
        return results
    
    def filter_results(self, results: List[Dict[str, Any]], 
                      min_duration: Optional[int] = None, 
                      max_duration: Optional[int] = None,
                      test_types: Optional[List[str]] = None,
                      remote_testing: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Filters search results based on criteria."""
        filtered = results.copy()
        
        
        if min_duration is not None or max_duration is not None:
            temp_filtered = []
            for result in filtered:
                duration_mins = self._parse_duration(result.get("duration", ""))
                if duration_mins is not None:
                    if min_duration is not None and duration_mins < min_duration:
                        continue
                    if max_duration is not None and duration_mins > max_duration:
                        continue
                temp_filtered.append(result)
            filtered = temp_filtered
        
        
        if test_types:
            filtered = [r for r in filtered if r.get("test_type") in test_types]
        
        # Filter by remote testing support
        if remote_testing is not None:
            filtered = [r for r in filtered if (r.get("remote_testing_support", "").lower() == "yes") == remote_testing]
        
        return filtered
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to minutes."""
        if not duration_str:
            return None
        
        duration_str = duration_str.lower()
        # Extract numbers
        numbers = re.findall(r'\d+', duration_str)
        
        try:
            if "hour" in duration_str:
                # Convert hours to minutes
                hours = float(numbers[0])
                minutes = 0
                if len(numbers) > 1:
                    minutes = int(numbers[1])
                return int(hours * 60 + minutes)
            else:
                # Assume minutes
                return int(numbers[0])
        except:
            return None
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocesses text for embedding."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
        
        # Simple tokenization by splitting on whitespace
        tokens = text.split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
                      'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than', 'such',
                      'when', 'while', 'who', 'with', 'at', 'from', 'for', 'to', 'by', 'about',
                      'against', 'between', 'into', 'through', 'during', 'before', 'after',
                      'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                      'again', 'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both',
                      'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                      'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
                      'should', 'now'}
        tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
        
        return tokens
    
    def _build_vocabulary(self, texts: List[str]):
        """Builds vocabulary from the texts."""
        word_freq = {}
        for text in texts:
            tokens = self._preprocess_text(text)
            for token in tokens:
                if token not in word_freq:
                    word_freq[token] = 0
                word_freq[token] += 1
        
        # Filter out rare words
        min_count = 2
        filtered_words = {word: freq for word, freq in word_freq.items() if freq >= min_count}
        
        # Create vocabulary with indices
        self.vocabulary = {word: idx for idx, word in enumerate(filtered_words.keys())}
        print(f"Built vocabulary with {len(self.vocabulary)} words")
    
    def _create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Creates embeddings for the texts using TF-IDF."""
        # Initialize embeddings array
        embeddings = np.zeros((len(texts), self.vector_size), dtype=np.float32)
        
        # Calculate document frequency for IDF
        doc_freq = {}
        for idx, text in enumerate(texts):
            tokens = self._preprocess_text(text)
            unique_tokens = set(tokens)
            for token in unique_tokens:
                if token in self.vocabulary:
                    if token not in doc_freq:
                        doc_freq[token] = 0
                    doc_freq[token] += 1
        
        # Calculate embeddings
        for idx, text in enumerate(texts):
            tokens = self._preprocess_text(text)
            token_counts = {}
            for token in tokens:
                if token in self.vocabulary:
                    if token not in token_counts:
                        token_counts[token] = 0
                    token_counts[token] += 1
            
            # Fill embedding vector using TF-IDF
            for token, count in token_counts.items():
                if token in self.vocabulary and token in doc_freq:
                    # Get vector index for this token
                    vec_idx = self.vocabulary[token] % self.vector_size
                    # Calculate TF-IDF
                    tf = count / len(tokens)
                    idf = np.log(len(texts) / (1 + doc_freq[token]))
                    tfidf = tf * idf
                    # Update embedding value
                    embeddings[idx, vec_idx] += tfidf
            
            # Normalize the vector
            norm = np.linalg.norm(embeddings[idx])
            if norm > 0:
                embeddings[idx] = embeddings[idx] / norm
        
        return embeddings
    
    def _embed_query(self, query: str) -> np.ndarray:
        """Embeds a query using the same method as the documents."""
        # Initialize query vector
        query_vector = np.zeros((1, self.vector_size), dtype=np.float32)
        
        # Process query
        tokens = self._preprocess_text(query)
        token_counts = {}
        for token in tokens:
            if token in self.vocabulary:
                if token not in token_counts:
                    token_counts[token] = 0
                token_counts[token] += 1
        
        # Fill query vector
        for token, count in token_counts.items():
            if token in self.vocabulary:
                # Get vector index for this token
                vec_idx = self.vocabulary[token] % self.vector_size
                # Simple TF score (we don't have IDF for the query)
                tf = count / len(tokens)
                # Update embedding value
                query_vector[0, vec_idx] += tf
        
        # Normalize the vector
        norm = np.linalg.norm(query_vector[0])
        if norm > 0:
            query_vector[0] = query_vector[0] / norm
        
        return query_vector