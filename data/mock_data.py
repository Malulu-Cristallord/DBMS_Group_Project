# =============================================================================
# FILE: data/mock_data.py
# PURPOSE: All mock data used across the Libtrack application.
#          When the back-end is ready, this data will be replaced by real
#          API calls (e.g., GET /api/books, GET /api/users, etc.)
# =============================================================================

# -----------------------------------------------------------------------------
# MOCK USER (logged-in user)
# In production: this comes from the authentication API after login.
# -----------------------------------------------------------------------------
CURRENT_USER = {
    "id": "usr_001",
    "username": "Marie L.",
    "initials": "ML",
    "email": "marie.lefebvre@email.com",
    "bio": "Passionate reader. Science fiction lover. Always on my next adventure between pages.",
    "member_since": "January 2024",
    "preferred_genres": ["Science fiction", "Fiction", "Philosophy"],
    "books_borrowed": 24,
    "posts_published": 8,
    "avg_rating": 4.2,
    "followers": 12,
    "badges": ["Avid reader", "Top reviewer", "Sci-fi fan", "Explorer"],
    "receive_recommendations": True,
    "public_profile": True,
    "show_borrowings": True,
    "show_reading_history": True,
    "allow_followers": True,
}

# -----------------------------------------------------------------------------
# MOCK BOOKS
# In production: this comes from GET /api/books
# Each book has a unique id, title, author, category, year, description,
# average rating, review count, available formats, and an external purchase URL.
# -----------------------------------------------------------------------------
BOOKS = [
    {
        "id": "book_001",
        "title": "Dune",
        "author": "Frank Herbert",
        "category": "Science fiction",
        "year": 1965,
        "description": (
            "On the desert planet Arrakis, the only source of the mysterious Spice, "
            "young Paul Atreides sees his life turned upside down when his family takes "
            "control of this resource coveted by the entire empire. A monumental work of "
            "science fiction that combines politics, ecology, religion, and adventure."
        ),
        "avg_rating": 4.8,
        "review_count": 312,
        "formats": ["Physical", "E-book"],
        "physical_available": "2 / 3",
        "ebook_available": True,
        "cover_color": "#3E7255",
        "purchase_url": "https://www.amazon.com",
        "popular": True,
    },
    {
        "id": "book_002",
        "title": "The Name of the Wind",
        "author": "Patrick Rothfuss",
        "category": "Fiction",
        "year": 2007,
        "description": (
            "The story of Kvothe — from his childhood in a troupe of traveling players, "
            "to his years spent as a near-feral orphan in a crime-ridden city, to his "
            "daringly brazen yet successful bid to enter a difficult and dangerous school "
            "of magic."
        ),
        "avg_rating": 4.7,
        "review_count": 198,
        "formats": ["Physical", "E-book"],
        "physical_available": "1 / 2",
        "ebook_available": True,
        "cover_color": "#654421",
        "purchase_url": "https://www.amazon.com",
        "popular": True,
    },
    {
        "id": "book_003",
        "title": "Foundation",
        "author": "Isaac Asimov",
        "category": "Science fiction",
        "year": 1951,
        "description": (
            "For twelve thousand years the Galactic Empire has ruled supreme. Now it is "
            "dying. Only Hari Seldon, creator of the revolutionary science of "
            "psychohistory, can see into the future — a dark age of ignorance, warfare, "
            "and violence that will last thirty thousand years."
        ),
        "avg_rating": 4.3,
        "review_count": 128,
        "formats": ["Physical", "E-book"],
        "physical_available": "3 / 3",
        "ebook_available": True,
        "cover_color": "#4A7FA5",
        "purchase_url": "https://www.amazon.com",
        "popular": True,
    },
    {
        "id": "book_004",
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "category": "History",
        "year": 2011,
        "description": (
            "100,000 years ago, at least six human species inhabited the earth. Today "
            "there is just one. Us. Homo sapiens. How did our species succeed in the "
            "battle for dominance? Why did our foraging ancestors come together to create "
            "cities and kingdoms?"
        ),
        "avg_rating": 4.8,
        "review_count": 241,
        "formats": ["Physical"],
        "physical_available": "0 / 2",
        "ebook_available": False,
        "cover_color": "#654421",
        "purchase_url": "https://www.amazon.com",
        "popular": True,
    },
    {
        "id": "book_005",
        "title": "1984",
        "author": "George Orwell",
        "category": "Fiction",
        "year": 1949,
        "description": (
            "Among the seminal texts of the 20th century, 1984 is a rare work that "
            "grows more haunting as its futuristic vision becomes more real. A startling "
            "and haunting vision of the world, 1984 is so powerful that it has become "
            "an expression of the modern age."
        ),
        "avg_rating": 4.6,
        "review_count": 405,
        "formats": ["Physical", "E-book"],
        "physical_available": "2 / 4",
        "ebook_available": True,
        "cover_color": "#3E7255",
        "purchase_url": "https://www.amazon.com",
        "popular": True,
    },
    {
        "id": "book_006",
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "category": "Fiction",
        "year": 1988,
        "description": (
            "Paulo Coelho's masterpiece tells the mystical story of Santiago, an "
            "Andalusian shepherd boy who yearns to travel in search of a worldly "
            "treasure. His quest will lead him to riches far different — and far greater "
            "— than he ever imagined."
        ),
        "avg_rating": 4.5,
        "review_count": 512,
        "formats": ["Physical", "E-book"],
        "physical_available": "1 / 3",
        "ebook_available": True,
        "cover_color": "#D2B354",
        "purchase_url": "https://www.amazon.com",
        "popular": False,
    },
    {
        "id": "book_007",
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "category": "Philosophy",
        "year": 180,
        "description": (
            "Written in Greek by the only philosopher-king of Rome, this is a series "
            "of spiritual exercises filled with Stoic philosophy and wisdom. A monument "
            "to Stoic philosophy, this is a practical work for everyone."
        ),
        "avg_rating": 4.9,
        "review_count": 87,
        "formats": ["Physical", "E-book"],
        "physical_available": "2 / 2",
        "ebook_available": True,
        "cover_color": "#8B7355",
        "purchase_url": "https://www.amazon.com",
        "popular": False,
    },
    {
        "id": "book_008",
        "title": "Steve Jobs",
        "author": "Walter Isaacson",
        "category": "Biography",
        "year": 2011,
        "description": (
            "Based on more than forty interviews with Jobs conducted over two years — "
            "as well as interviews with more than a hundred family members, friends, "
            "adversaries, competitors, and colleagues — Walter Isaacson has written a "
            "riveting story of the roller-coaster life and searingly intense personality "
            "of a creative entrepreneur."
        ),
        "avg_rating": 4.1,
        "review_count": 163,
        "formats": ["Physical"],
        "physical_available": "1 / 2",
        "ebook_available": False,
        "cover_color": "#3A3A3A",
        "purchase_url": "https://www.amazon.com",
        "popular": False,
    },
]

# -----------------------------------------------------------------------------
# MOCK REVIEWS
# In production: this comes from GET /api/reviews?book_id=...
# -----------------------------------------------------------------------------
REVIEWS = [
    {
        "id": "rev_001",
        "book_id": "book_001",
        "user": "John Dupont",
        "initials": "JD",
        "avatar_color": "#DFF2DF",
        "text_color": "#3E7255",
        "rating": 5,
        "text": "An absolute masterpiece. The world-building is incredibly rich, and the characters feel deeply human despite the sci-fi setting.",
        "time_ago": "3 days ago",
    },
    {
        "id": "rev_002",
        "book_id": "book_001",
        "user": "Sophie Martin",
        "initials": "SM",
        "avatar_color": "#EFE5DA",
        "text_color": "#654421",
        "rating": 4,
        "text": "A demanding but incredibly rewarding read. I'd recommend pushing through the first 100 pages.",
        "time_ago": "1 week ago",
    },
    {
        "id": "rev_003",
        "book_id": "book_002",
        "user": "Alex Chen",
        "initials": "AC",
        "avatar_color": "#DFF2DF",
        "text_color": "#3E7255",
        "rating": 5,
        "text": "A story that grabs you from the first pages. Kvothe is an unforgettable character. I never thought I'd be so hooked on a fantasy novel.",
        "time_ago": "2 hours ago",
    },
    {
        "id": "rev_004",
        "book_id": "book_003",
        "user": "Marie L.",
        "initials": "ML",
        "avatar_color": "#D2B354",
        "text_color": "#654421",
        "rating": 4,
        "text": "A foundational work of science fiction. Asimov's vision of the future is both humbling and inspiring.",
        "time_ago": "5 days ago",
    },
]

# -----------------------------------------------------------------------------
# MOCK POSTS (Community Feed)
# In production: this comes from GET /api/posts
# -----------------------------------------------------------------------------
POSTS = [
    {
        "id": "post_001",
        "user": "Sophie Martin",
        "initials": "SM",
        "avatar_color": "#EFE5DA",
        "text_color": "#654421",
        "action": "rated",
        "book_title": "The Name of the Wind",
        "book_id": "book_002",
        "time_ago": "2h ago",
        "rating": 5,
        "content": "A story that grabs you from the first pages. Kvothe is an unforgettable character. I never thought I'd be so hooked on a fantasy novel.",
        "likes": 14,
        "comments": 3,
        "format_tag": None,
    },
    {
        "id": "post_002",
        "user": "John Dupont",
        "initials": "JD",
        "avatar_color": "#DFF2DF",
        "text_color": "#3E7255",
        "action": "borrowed",
        "book_title": "Sapiens",
        "book_id": "book_004",
        "time_ago": "yesterday",
        "rating": None,
        "content": "Finally! This book has been on my list for months. Can't wait to dive in this weekend.",
        "likes": 7,
        "comments": 1,
        "format_tag": "Physical",
    },
    {
        "id": "post_003",
        "user": "Thomas G.",
        "initials": "TG",
        "avatar_color": "#D2B354",
        "text_color": "#654421",
        "action": "reviewed",
        "book_title": "Dune",
        "book_id": "book_001",
        "time_ago": "3 days ago",
        "rating": 5,
        "content": "A masterpiece of sci-fi, impossible to put down. The politics, the ecology, the religion — it all weaves together perfectly.",
        "likes": 22,
        "comments": 5,
        "format_tag": None,
    },
    {
        "id": "post_004",
        "user": "Léa Bernard",
        "initials": "LB",
        "avatar_color": "#DFF2DF",
        "text_color": "#1F3F2E",
        "action": "reviewed",
        "book_title": "1984",
        "book_id": "book_005",
        "time_ago": "4 days ago",
        "rating": 5,
        "content": "Terrifyingly relevant even today. Orwell's vision of surveillance and control feels more prescient than ever.",
        "likes": 18,
        "comments": 7,
        "format_tag": "E-book",
    },
]

# -----------------------------------------------------------------------------
# MOCK BORROWINGS (Current loans)
# In production: this comes from GET /api/borrowings?user_id=...
# -----------------------------------------------------------------------------
CURRENT_BORROWINGS = [
    {
        "id": "bor_001",
        "book_id": "book_001",
        "title": "Dune",
        "author": "Frank Herbert",
        "format": "Physical",
        "due_date": "April 28, 2026",
        "days_remaining": 12,
        "total_days": 30,
        "cover_color": "#3E7255",
    },
    {
        "id": "bor_002",
        "book_id": "book_003",
        "title": "Foundation",
        "author": "Isaac Asimov",
        "format": "E-book",
        "due_date": "May 5, 2026",
        "days_remaining": 25,
        "total_days": 30,
        "cover_color": "#4A7FA5",
    },
]

# -----------------------------------------------------------------------------
# MOCK RESERVATIONS (Pending)
# In production: this comes from GET /api/reservations?user_id=...
# -----------------------------------------------------------------------------
PENDING_RESERVATIONS = [
    {
        "id": "res_001",
        "book_id": "book_004",
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "queue_position": 2,
        "estimated_days": 5,
        "cover_color": "#654421",
    },
]

# -----------------------------------------------------------------------------
# MOCK READING HISTORY
# In production: this comes from GET /api/history?user_id=...
# -----------------------------------------------------------------------------
READING_HISTORY = [
    {
        "id": "hist_001",
        "book_id": "book_003",
        "title": "Foundation",
        "author": "Isaac Asimov",
        "borrowed_date": "Apr 10",
        "returned_date": "Apr 24",
        "format": "E-book",
        "month": "APRIL 2026",
        "rating": 4,
        "cover_color": "#4A7FA5",
    },
    {
        "id": "hist_002",
        "book_id": "book_001",
        "title": "Dune",
        "author": "Frank Herbert",
        "borrowed_date": "Mar 3",
        "returned_date": "Mar 20",
        "format": "Physical",
        "month": "MARCH 2026",
        "rating": 5,
        "cover_color": "#3E7255",
    },
    {
        "id": "hist_003",
        "book_id": "book_004",
        "title": "Sapiens",
        "author": "Yuval Noah Harari",
        "borrowed_date": "Mar 1",
        "returned_date": "Mar 18",
        "format": "Physical",
        "month": "MARCH 2026",
        "rating": 5,
        "cover_color": "#654421",
    },
    {
        "id": "hist_004",
        "book_id": "book_005",
        "title": "1984",
        "author": "George Orwell",
        "borrowed_date": "Feb 5",
        "returned_date": "Feb 22",
        "format": "E-book",
        "month": "FEBRUARY 2026",
        "rating": 5,
        "cover_color": "#3E7255",
    },
]

# -----------------------------------------------------------------------------
# MOCK LEADERBOARD (Most Active Readers)
# In production: this comes from GET /api/leaderboard
# -----------------------------------------------------------------------------
LEADERBOARD = [
    {
        "rank": 1,
        "user": "Thomas G.",
        "initials": "TG",
        "avatar_color": "#D2B354",
        "text_color": "#654421",
        "books_this_month": 18,
        "badge": "Gold",
        "badge_color": "#D2B354",
        "is_current_user": False,
    },
    {
        "rank": 2,
        "user": "Sophie M.",
        "initials": "SM",
        "avatar_color": "#EFE5DA",
        "text_color": "#654421",
        "books_this_month": 14,
        "badge": "Silver",
        "badge_color": "#8A8A8A",
        "is_current_user": False,
    },
    {
        "rank": 3,
        "user": "Marie L.",
        "initials": "ML",
        "avatar_color": "#D2B354",
        "text_color": "#654421",
        "books_this_month": 12,
        "badge": None,
        "badge_color": None,
        "is_current_user": True,
    },
    {
        "rank": 4,
        "user": "Alex C.",
        "initials": "AC",
        "avatar_color": "#DFF2DF",
        "text_color": "#3E7255",
        "books_this_month": 9,
        "badge": None,
        "badge_color": None,
        "is_current_user": False,
    },
]

# Most borrowed books (for stats page)
MOST_BORROWED = [
    {"rank": 1, "title": "Dune", "author": "Frank Herbert", "borrowings": 87, "book_id": "book_001", "cover_color": "#3E7255"},
    {"rank": 2, "title": "Sapiens", "author": "Y. N. Harari", "borrowings": 74, "book_id": "book_004", "cover_color": "#654421"},
    {"rank": 3, "title": "Foundation", "author": "I. Asimov", "borrowings": 61, "book_id": "book_003", "cover_color": "#4A7FA5"},
    {"rank": 4, "title": "The Name of the Wind", "author": "P. Rothfuss", "borrowings": 54, "book_id": "book_002", "cover_color": "#654421"},
]

# Platform-wide statistics
PLATFORM_STATS = {
    "active_readers": 1248,
    "borrowings_this_month": 8432,
    "reviews_published": 2156,
    "available_titles": 94,
}

# Genre list (used in filters and registration)
GENRES = ["All genres", "Fiction", "Science fiction", "History", "Biography", "Philosophy", "Art & Design", "Mystery", "Romance", "Self-help"]

# Badge definitions for rewards page
ALL_BADGES = [
    {"name": "Avid reader", "description": "Borrow 10+ books", "earned": True, "color_bg": "#DFF2DF", "color_text": "#1F3F2E", "progress": 100},
    {"name": "Top reviewer", "description": "Write 5+ reviews", "earned": True, "color_bg": "#D2B354", "color_text": "#654421", "progress": 100},
    {"name": "Sci-fi fan", "description": "Read 5+ sci-fi books", "earned": True, "color_bg": "#EFE5DA", "color_text": "#654421", "progress": 100},
    {"name": "Explorer", "description": "Read 3+ different genres", "earned": True, "color_bg": "#DFF2DF", "color_text": "#1F3F2E", "progress": 100},
    {"name": "Bookworm", "description": "Borrow 25+ books", "earned": False, "color_bg": "#F5F5F5", "color_text": "#8A8A8A", "progress": 96},
    {"name": "Social reader", "description": "Get 50+ likes on posts", "earned": False, "color_bg": "#F5F5F5", "color_text": "#8A8A8A", "progress": 62},
    {"name": "Gold badge", "description": "Reach top 1 on leaderboard", "earned": False, "color_bg": "#F5F5F5", "color_text": "#8A8A8A", "progress": 33},
]

# Wishlist items
WISHLIST = [
    {"book_id": "book_006", "title": "The Alchemist", "author": "Paulo Coelho", "cover_color": "#D2B354"},
    {"book_id": "book_007", "title": "Meditations", "author": "Marcus Aurelius", "cover_color": "#8B7355"},
]