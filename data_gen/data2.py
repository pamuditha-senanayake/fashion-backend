import psycopg2
import random
from datetime import datetime, timedelta

# --- Connect to PostgreSQL database ---
conn = psycopg2.connect(
    host="localhost",
    database="fashionsite",
    user="pamudithasenanayake",
    password="123"
)
cur = conn.cursor()

# --- Trend names and types ---
trend_names = ["oversized jacket", "neon colors", "bucket hat", "plaid skirt", "sneaker trend",
               "crop top", "denim overalls", "streetwear hoodie", "leather boots", "floral dress"]
trend_types = ["style", "color", "accessory", "pattern", "footwear", "style", "style", "style", "footwear", "style"]

# --- Hashtags and descriptive templates ---
hashtags_pool = ["#fashion", "#style", "#trend", "#OOTD", "#streetwear", "#summer", "#vintage", "#chic"]
descriptive_texts = [
    "Absolutely loving my {} today!",
    "Check out this {} outfit I styled for the weekend.",
    "Feeling so trendy in my new {}.",
    "Can't get enough of {} this season!",
    "My favorite pick for this week: {}.",
    "Street style vibes with {}.",
    "Casual yet stylish look featuring {}.",
    "Rocking {} for a night out.",
    "Summer fashion just got better with {}.",
    "Here's how I styled {} this week."
]

tags_pool = ["casual", "summer", "vintage", "street", "modern", "chic", "edgy", "minimal", "boho", "sporty"]

# --- Forecasting / visualization support ---
trend_directions = ["rising", "stable", "falling"]  # For future visualization arrows

# --- Number of posts to generate ---
num_posts = 200

# --- Optional: Placeholder for social media API fetching ---
def fetch_real_posts(platform="twitter"):
    """
    Placeholder function for future API integration.
    You could fetch real posts here instead of generating synthetic ones.
    Returns list of dicts with keys: content, media_url, timestamp, likes, shares, comments
    """
    return []  # Empty for now, using synthetic data

# --- Generate synthetic fashion posts ---
for _ in range(num_posts):
    trend_idx = random.randint(0, len(trend_names) - 1)
    trend_name = trend_names[trend_idx]
    trend_type = trend_types[trend_idx]

    # --- Content generation ---
    content = random.choice(descriptive_texts).format(trend_name)
    media_url = f"http://example.com/media{random.randint(1, 500)}.jpg"
    hashtags = random.sample(hashtags_pool, k=random.randint(1, 4))
    tags = random.sample(tags_pool, k=3)

    # --- Temporal / timestamp for forecasting ---
    timestamp = datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))

    # --- Engagement metrics ---
    likes = random.randint(5, 500)
    shares = random.randint(1, 100)
    comments = random.randint(0, 50)

    # --- Trend score calculation (can be used in ML models for forecasting) ---
    frequency_score = random.uniform(0.1, 1.0)
    engagement_score = (0.4 * likes + 0.3 * shares + 0.3 * comments) / 500
    recency_score = 1.0 - (datetime.now() - timestamp).days / 90  # Decay factor for older posts
    trend_score = round(0.5 * frequency_score + 0.4 * engagement_score + 0.1 * recency_score, 2)

    # --- Determine trend direction for visualization (simple heuristic) ---
    if trend_score > 0.7:
        trend_direction = "rising"
    elif trend_score > 0.4:
        trend_direction = "stable"
    else:
        trend_direction = "falling"

    # --- Insert into DB ---
    cur.execute("""
        INSERT INTO synthetic_fashion_trends
        (content, media_url, hashtags, timestamp, likes, shares, comments, trend_name, trend_type, trend_score,
         tags, trend_direction)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (content, media_url, hashtags, timestamp, likes, shares, comments,
         trend_name, trend_type, trend_score, tags, trend_direction)
    )

# --- Commit and close ---
conn.commit()
cur.close()
conn.close()

print(f"{num_posts} synthetic fashion posts with temporal and trend data inserted successfully!")
