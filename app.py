import streamlit as st
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="📚 My Book Collection Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stats-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

class BookCollection:
    def __init__(self):
        self.books_list = []
        self.storage_file = "books.json"
        self.read_from_file()

    def read_from_file(self):
        try:
            with open(self.storage_file, "r") as file:
                self.books_list = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.books_list = []

    def save_to_file(self):
        with open(self.storage_file, "w") as file:
            json.dump(self.books_list, file, indent=4)

    def add_book(self, title, author, year, genre, read):
        new_book = {
            "title": title,
            "author": author,
            "year": year,
            "genre": genre,
            "read": read,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }
        self.books_list.append(new_book)
        self.save_to_file()

    def delete_book(self, title):
        self.books_list = [book for book in self.books_list if book["title"].lower() != title.lower()]
        self.save_to_file()

    def update_book(self, title, new_data):
        for book in self.books_list:
            if book["title"].lower() == title.lower():
                book.update(new_data)
                self.save_to_file()
                return True
        return False

    def get_reading_stats(self):
        total_books = len(self.books_list)
        completed_books = sum(1 for book in self.books_list if book["read"])
        completion_rate = (completed_books / total_books * 100) if total_books > 0 else 0
        return total_books, completed_books, completion_rate

# Initialize the book collection
if 'book_collection' not in st.session_state:
    st.session_state.book_collection = BookCollection()

# Sidebar
with st.sidebar:
    st.title("📚 Book Collection Manager")
    menu = st.radio(
        "Navigation",
        ["Add Book", "View Collection", "Search Books", "Reading Stats"]
    )

# Main content
if menu == "Add Book":
    st.header("Add New Book")
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            year = st.number_input("Publication Year", min_value=1800, max_value=datetime.now().year)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science Fiction", "Mystery", "Romance", "Other"])
            read = st.checkbox("I have read this book")
        
        if st.form_submit_button("Add Book"):
            if title and author:
                st.session_state.book_collection.add_book(title, author, year, genre, read)
                st.success(f"Book '{title}' has been added to your collection!")
                st.rerun()
            else:
                st.error("Please fill in all required fields!")

elif menu == "View Collection":
    st.header("Your Book Collection")
    
    # Search and filter options
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search books", "")
    with col2:
        filter_genre = st.selectbox("Filter by genre", ["All"] + list(set(book["genre"] for book in st.session_state.book_collection.books_list)))

    # Display books
    for book in st.session_state.book_collection.books_list:
        if (search_term.lower() in book["title"].lower() or search_term.lower() in book["author"].lower()) and \
           (filter_genre == "All" or book["genre"] == filter_genre):
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        <div class="book-card">
                            <h3>{book['title']}</h3>
                            <p>Author: {book['author']} | Year: {book['year']} | Genre: {book['genre']}</p>
                            <p>Status: {'✅ Read' if book['read'] else '📖 Unread'}</p>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Delete", key=f"delete_{book['title']}"):
                        st.session_state.book_collection.delete_book(book["title"])
                        st.rerun()

elif menu == "Search Books":
    st.header("Search Books")
    search_type = st.radio("Search by", ["Title", "Author"])
    search_term = st.text_input("Enter search term")
    
    if search_term:
        results = []
        for book in st.session_state.book_collection.books_list:
            if search_type == "Title" and search_term.lower() in book["title"].lower():
                results.append(book)
            elif search_type == "Author" and search_term.lower() in book["author"].lower():
                results.append(book)
        
        if results:
            for book in results:
                st.markdown(f"""
                    <div class="book-card">
                        <h3>{book['title']}</h3>
                        <p>Author: {book['author']} | Year: {book['year']} | Genre: {book['genre']}</p>
                        <p>Status: {'✅ Read' if book['read'] else '📖 Unread'}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No books found matching your search criteria.")

else:  # Reading Stats
    st.header("Reading Statistics")
    
    total_books, completed_books, completion_rate = st.session_state.book_collection.get_reading_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="stats-card">
                <h3>Total Books</h3>
                <h2>{total_books}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stats-card">
                <h3>Books Read</h3>
                <h2>{completed_books}</h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stats-card">
                <h3>Completion Rate</h3>
                <h2>{completion_rate:.1f}%</h2>
            </div>
        """, unsafe_allow_html=True)
    
    # Genre distribution
    st.subheader("Genre Distribution")
    genres = {}
    for book in st.session_state.book_collection.books_list:
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
    
    if genres:
        st.bar_chart(genres)
    else:
        st.info("No books in your collection yet.") 