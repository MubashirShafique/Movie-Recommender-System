
import pickle
import streamlit as st

# -------------------------------
# Load enriched dataset
# -------------------------------
movies = pickle.load(open('3_Models/movies_with_full_details.pkl', 'rb'))
similarity = pickle.load(open('3_Models/similarity.pkl', 'rb'))

# -------------------------------
# Helper Functions
# -------------------------------
def get_movie_details(movie_id):
    """Fetch movie details from local enriched dataset"""
    movie = movies[movies['id'] == movie_id].iloc[0]
    
    return {
        "poster": movie.get("poster_url", "https://via.placeholder.com/150"),
        "title": movie.get("original_title", "Unknown"),
        "release_date": movie.get("release_date", "N/A"),
        "rating": movie.get("rating", "N/A"),
        "overview": movie.get("overview", "No description available."),
        "tagline": movie.get("tagline", ""),
        "runtime": movie.get("runtime", 0),
        "genres": movie.get("genres", "N/A").split(", ") if movie.get("genres") else []
    }

def recommend(movie, n=15):
    """Recommend N similar movies"""
    index = movies[movies['original_title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended = []
    for i in distances[1:n+1]:
        movie_id = movies.iloc[i[0]].id
        details = get_movie_details(movie_id)
        recommended.append(details)
    return recommended


# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")


if "selected_movie" not in st.session_state:
    st.header("🎬 Movie Recommender System")

    selected_movie_name = st.selectbox('Search for a Movie:', movies['original_title'].values)

    if st.button('Search'):
        st.session_state.selected_movie = selected_movie_name
        st.rerun()

    # -------------------------------
    # Pagination Settings
    # -------------------------------
    movies_per_page = 500
    total_movies = len(movies)
    total_pages = (total_movies // movies_per_page) + (1 if total_movies % movies_per_page != 0 else 0)

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    # Page Navigation (Prev / Next + Page Numbers)
    nav_cols = st.columns([1, 6, 1])
    with nav_cols[0]:
        if st.button("⬅ Prev") and st.session_state.current_page > 1:
            st.session_state.current_page -= 1
            st.rerun()
    with nav_cols[1]:
        page_buttons = st.columns(min(total_pages, 10))  # max 10 buttons
        for i in range(1, min(total_pages + 1, 11)):
            if page_buttons[i-1].button(str(i), key=f"page_{i}"):
                st.session_state.current_page = i
                st.rerun()
        st.markdown(f"**Page {st.session_state.current_page} of {total_pages}**")
    with nav_cols[2]:
        if st.button("Next ➡") and st.session_state.current_page < total_pages:
            st.session_state.current_page += 1
            st.rerun()

    # Slice movies for current page
    start_idx = (st.session_state.current_page - 1) * movies_per_page
    end_idx = start_idx + movies_per_page
    page_movies = movies.iloc[start_idx:end_idx]

    # -------------------------------
    # Show movies in grid
    # -------------------------------
    cols = st.columns(5)
    for i, movie in enumerate(page_movies.itertuples()):
        with cols[i % 5]:
            details = get_movie_details(movie.id)
            
            # Poster clickable
            st.markdown(
                f'<a href="?movie={movie.original_title}"><img src="{details["poster"]}" width="150"></a>', 
                unsafe_allow_html=True
            )

            # Title button
            if st.button(movie.original_title, key=f"title_{start_idx + i}"):
                st.session_state.selected_movie = movie.original_title
                st.rerun()


else:
    selected_movie = st.session_state.selected_movie
    st.title(f"🎥 {selected_movie}")
    
    movie_id = movies[movies['original_title'] == selected_movie].iloc[0].id
    details = get_movie_details(movie_id)

    # Show movie info
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(details["poster"], width=300)
    with col2:
        if details["tagline"]:
            st.subheader(details["tagline"])
        st.write(f"⭐ **Rating:** {details['rating']}")
        st.write(f"📅 **Release Date:** {details['release_date']}")
        st.write(f"🎭 **Genres:** {', '.join(details['genres']) if details['genres'] else 'N/A'}")
        st.write(f"⏱ **Runtime:** {details['runtime']} min")
        st.write(f"📝 **Overview:** {details['overview']}")

    # Recommended Movies
    st.subheader("✨ Recommended Movies")
    recommended_movies = recommend(selected_movie, n=15)

    for row in range(0, 15, 5):
        cols = st.columns(5)
        for i in range(5):
            idx = row + i
            movie = recommended_movies[idx]
            with cols[i]:
                st.markdown(
                    f"""
                    <a href="?movie={movie['title']}">
                        <img src="{movie['poster']}" width="150">
                    </a>
                    """, unsafe_allow_html=True
                )
                if st.button(movie['title'], key=f"rec_title_{idx}"):
                    st.session_state.selected_movie = movie['title']
                    st.rerun()

    # Back Button
    if st.button("⬅ Back to All Movies"):
        del st.session_state.selected_movie
        st.rerun()
