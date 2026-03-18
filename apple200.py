import pickle
import streamlit as st
import requests
import os
API_KEY = "6ff81781a63ac2a231cf6b7cfc6ca8d2"
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess

# Use absolute paths relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_data():
    movie_path = os.path.join(BASE_DIR, 'movies.pkl')
    sim_path = os.path.join(BASE_DIR, 'similarity.pkl')
    
    with open(movie_path, 'rb') as f:
        movies = pickle.load(f)
    with open(sim_path, 'rb') as f:
        similarity = pickle.load(f)
        
    return movies, similarity

movies, similarity = load_data()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---- session with retry ----
session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": API_KEY, "language": "en-US"}

    try:
        r = session.get(
            url,
            params=params,
            timeout=5,
            verify=False
        )

        if r.status_code != 200:
            return PLACEHOLDER

        data = r.json()
        poster = data.get("poster_path")

        if not poster:
            return PLACEHOLDER

        return "https://image.tmdb.org/t/p/w500" + poster

    except requests.exceptions.RequestException:
        # 🔥 catches SSL, reset, timeout, proxy, EVERYTHING
        return PLACEHOLDER

def recommend(movie):
    index = movies[movies['Title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].Title)

    return recommended_movie_names,recommended_movie_posters


st.header('Movie Recommender System')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
movies = pickle.load(open(os.path.join(BASE_DIR, 'movies.pkl'), 'rb'))
similarity = pickle.load(open(os.path.join(BASE_DIR, 'similarity.pkl'), 'rb'))


movie_list = movies['Title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown",movie_list)

if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])




