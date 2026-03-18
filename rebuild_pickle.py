import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import numpy as np
import os

# Helper functions to clean metadata
def convert(obj):
    try:
        L = [i['name'] for i in ast.literal_eval(obj)]
        return [i.replace(" ", "") for i in L]
    except:
        return []

def convert_cast(obj):
    try:
        L = []
        counter = 0
        for i in ast.literal_eval(obj):
            if counter != 3:
                L.append(i['name'].replace(" ", ""))
                counter += 1
            else:
                break
        return L
    except:
        return []

def fetch_director(obj):
    try:
        for i in ast.literal_eval(obj):
            if i['job'] == 'Director':
                return [i['name'].replace(" ", "")]
        return []
    except:
        return []

def rebuild():
    print("🎬 Starting optimized data processing...")
    
    # 1. Load raw datasets
    if not os.path.exists('tmdb_5000_movies.csv') or not os.path.exists('tmdb_5000_credits.csv'):
        print("❌ Error: CSV files not found in the current directory.")
        return

    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
    
    # 2. Merge and select necessary columns
    movies = movies.merge(credits, on='title')
    movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
    movies.dropna(inplace=True)
    
    # 3. Clean and Transform Data
    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(convert_cast)
    movies['crew'] = movies['crew'].apply(fetch_director)
    movies['overview'] = movies['overview'].apply(lambda x: x.split())
    
    # 4. Create tags for the recommendation engine
    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
    new_df = movies[['movie_id', 'title', 'tags']].copy()
    new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())
    
    # --- CRITICAL: Match the 'Title' column used in apple200.py ---
    new_df.rename(columns={'title': 'Title'}, inplace=True)
    
    # 5. Vectorization (Reduced features to save RAM)
    print("🤖 Vectorizing and calculating similarity...")
    cv = CountVectorizer(max_features=3000, stop_words='english')
    vectors = cv.fit_transform(new_df['tags']).toarray().astype(np.float32)
    
    # Calculate similarity matrix
    similarity = cosine_similarity(vectors)
    
    # 6. Save as Pickle files
    print("💾 Saving movies.pkl and similarity.pkl...")
    with open('movies.pkl', 'wb') as f:
        pickle.dump(new_df, f)
    with open('similarity.pkl', 'wb') as f:
        pickle.dump(similarity, f)
        
    print("✅ Success! Files are ready for deployment.")

if __name__ == "__main__":
    rebuild()