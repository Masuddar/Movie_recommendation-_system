import streamlit as st
import pickle
import pandas as pd
import requests
import json
import http.client

# GPT-4 Turbo API key (from RapidAPI)
rapidapi_key = 'bb2fe6bbcbmsh22d6e5c6ebf0387p17a611jsn0466f711ebcf'

# Function to fetch movie details (poster, overview, release date, rating)
def fetch_movie_details(movie_id):
    api_key = 'd1aa405518bcd86047c245cdc2bfe4e5'
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}')
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx/5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return None, "Error fetching movie details.", "N/A", "N/A"

    poster_path = "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')
    overview = data.get('overview', 'No overview available.')
    release_date = data.get('release_date', 'N/A')
    rating = data.get('vote_average', 'N/A')
    return poster_path, overview, release_date, rating

# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, overview, release_date, rating = fetch_movie_details(movie_id)

        recommended_movies.append({
            'title': title,
            'poster': poster,
            'overview': overview,
            'release_date': release_date,
            'rating': rating
        })

    return recommended_movies

# GPT-4 Turbo API request function via RapidAPI
def gpt_rapidapi_request(prompt):
    conn = http.client.HTTPSConnection("cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com")

    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "model": "gpt-4o",
        "max_tokens": 100,
        "temperature": 0.9
    })

    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "cheapest-gpt-4-turbo-gpt-4-vision-chatgpt-openai-ai-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()

    response_json = json.loads(data.decode("utf-8"))
    if 'choices' in response_json and len(response_json['choices']) > 0:
        return response_json['choices'][0]['message']['content']
    else:
        return "Sorry, I couldn't process the request. 😔"

# Load data for movie recommendations
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Custom CSS Styling for Streamlit
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    body {
        background: url('Gbackground.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Montserrat', sans-serif;
        color: #E0E0E0;
    }
    .header {
        text-align: center;
        padding: 20px;
        background-color: rgba(0, 0, 0, 0.4);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    }
    .header h1 {
        font-size: 50px;
    }
    .header h4 {
        font-size: 20px;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(68, 68, 68, 0.8);
        color: white;
        text-align: center;
        padding: 2px;
        font-size: 10px;
        border-top: 2px solid #FFD700;
    }
    .stButton>button {
        background-color: #FFD700 !important;
        color: black;
        border: none;
        padding: 12px 28px;
        text-align: center;
        border-radius: 25px;
        transition: all 0.3s ease;
        cursor: pointer;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #FFC700 !important;
        transform: scale(1.05);
    }
    .stSelectbox label {
        font-size: 20px;
        font-weight: bold;
    }
    .stImage img {
        border-radius: 15px;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stImage img:hover {
        transform: scale(1.05);
    }
    .movie-title {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
    }
    .movie-info {
        font-size: 16px;
        padding: 10px;
        text-align: justify;
    }
    </style>
""", unsafe_allow_html=True)

# Header with transparent background
st.markdown('<div class="header"><h1>Find your movie 🎬🍿</h1><h4>Discover your next favorite film 📽️</h4></div>',
            unsafe_allow_html=True)

# Movie Recommendation Section
option = st.selectbox('Choose a movie to get recommendations 🎥:', movies['title'].values)

if st.button('Recommend 🎬'):
    recommended_movies = recommend(option)

    # Display recommended movies
    for movie in recommended_movies:
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(movie['poster'])

        with col2:
            st.markdown(f"<div class='movie-title'>🎞️ {movie['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'><b>🎬 Release Date:</b> {movie['release_date']}</div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'><b>⭐ Rating:</b> {movie['rating']} / 10</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='movie-info'><b>📝 Overview:</b> {movie['overview']}</div>", unsafe_allow_html=True)

# GPT-4 Chatbot Section
st.markdown('<h2>Chat with MovieBot 🤖🍿</h2>', unsafe_allow_html=True)

user_input = st.text_input("Ask MovieBot anything (e.g., 'What is the best movie in 2023?') 💬")

if st.button('Ask MovieBot 🎤'):
    if user_input:
        chatbot_response = gpt_rapidapi_request(user_input)
        st.markdown(f"<div class='movie-info'><b>MovieBot:</b> {chatbot_response} 🤖</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='movie-info'><b>MovieBot:</b> Please type a question. ❓</div>", unsafe_allow_html=True)

# Footer with Credits
st.markdown("""
    <div class="footer">
    <p>Developed by Masuddar Rahaman | © 2024 Movie Recommender System 🎥</p>
    </div>
""", unsafe_allow_html=True)
