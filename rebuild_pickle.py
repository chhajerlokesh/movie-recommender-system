import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name']) 
    return L

def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

def rebuild():
    print("Starting data processing...")
    
    # 1. Load Data
    movies = pd.read_csv('tmdb_5000_movies.csv')
    credits = pd.read_csv('tmdb_5000_credits.csv')
    
    # 2. Merge
    movies = movies.merge(credits, on='title')
    
    # 3. Select columns
    movies = movies[['movie_id','title','overview','genres','keywords','cast','crew']]
    movies.dropna(inplace=True)
    
    # 4. Clean Data
    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(convert3)
    movies['crew'] = movies['crew'].apply(fetch_director)
    
    movies['overview'] = movies['overview'].apply(lambda x:x.split())
    movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
    movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
    movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ","") for i in x])
    movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])
    
    # 5. Create Tags
    movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
    new_df = movies[['movie_id','title','tags']]
    new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
    new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())
    
    # 6. Vectorization & Similarity
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(new_df['tags']).toarray()
    similarity = cosine_similarity(vectors)
    
    # 7. Save Files
    print("Saving pickle files...")
    pickle.dump(new_df, open('movies.pkl','wb'))
    pickle.dump(similarity, open('similarity.pkl','wb'))
    print("Done! Files created successfully.")

if __name__ == "__main__":
    rebuild()