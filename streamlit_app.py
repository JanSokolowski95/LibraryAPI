import streamlit as st
import requests
import os

# Get the API URL from environment variables
API_URL = os.getenv("API_URL", "http://api:8000")

st.set_page_config(page_title="Library Management System", layout="wide")
st.title("Library Management System")
st.markdown("Use this interface to manage your book inventory via the FastAPI backend.")


# --- Helper function to interact with the API ---
def call_api(method, endpoint, data=None):
    try:
        url = f"{API_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "GET":
            response = requests.get(url)

        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {e}")
        return None


# --- Main UI Layout ---


def on_change():
    st.session_state.is_checked = not st.session_state.is_checked


def refresh():
    st.session_state.books = call_api("GET", "/books/")


view_tab, add_tab, update_tab, delete_tab = st.tabs(
    ["View all the books", "Add a book", "Update a book", "Delete a book"]
)

with view_tab:
    st.header("All Books in the Library")
    if "books" not in st.session_state:
        st.session_state.books = call_api("GET", "/books/")
    if st.session_state.books:
        st.table(st.session_state.books)
    st.button("Refresh data", on_click=refresh)


with add_tab:
    st.header("Add a New Book")
    with st.form("add_book_form"):
        book_id = st.text_input("Book ID (6-digit unique ID)")
        title = st.text_input("Title")
        author = st.text_input("Author")
        submitted = st.form_submit_button("Add Book")

        if submitted:
            if not (book_id and title and author):
                st.warning("Please fill out all fields.")
            elif not book_id.isnumeric():
                st.warning("Please procide the correct ID (digits only)")
            else:
                data = {"book_id": book_id, "title": title, "author": author}
                response = call_api("POST", "/books/", data=data)
                if response:
                    st.success(f"Book '{title}' added successfully!")
                    st.json(response)

with update_tab:
    if "is_checked" not in st.session_state:
        st.session_state.is_checked = False
    st.header("Update Book Status")
    is_borrowed = st.toggle(
        label="A book got borrowed"
        if st.session_state.is_checked
        else "A book got returned",
        value=st.session_state.is_checked,
        on_change=on_change,
    )
    with st.form("update_book_form"):
        book_id = st.text_input("Book ID to update")
        borrower_id = st.text_input("Borrower ID", disabled=not is_borrowed)
        submitted = st.form_submit_button("Update Status")

        if submitted:
            if not book_id:
                st.warning("Please enter a Book ID.")
            else:
                data = {
                    "is_borrowed": is_borrowed,
                    "borrower_id": borrower_id if is_borrowed else None,
                }
                response = call_api("PUT", f"/books/{book_id}", data=data)
                if response:
                    st.success(f"Status for book '{book_id}' updated successfully!")
                    st.json(response)

with delete_tab:
    st.header("Delete a Book")
    with st.form("delete_book_form"):
        book_id = st.text_input("Book ID to delete")
        submitted = st.form_submit_button("Delete Book")

        if submitted:
            if not book_id:
                st.warning("Please enter a Book ID.")
            else:
                response = call_api("DELETE", f"/books/{book_id}")
                if response:
                    st.success(f"Book with ID '{book_id}' deleted successfully!")
