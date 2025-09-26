import psycopg2
import random
from datetime import datetime, timedelta

# --- Connect to your PostgreSQL database ---
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

# --- Hashtags and descriptive words ---
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

# --- Generate synthetic data ---
num_posts = 200  # Number of posts to generate
for _ in range(num_posts):
    trend_idx = random.randint(0, len(trend_names) - 1)
    trend_name = trend_names[trend_idx]
    trend_type = trend_types[trend_idx]

    content = random.choice(descriptive_texts).format(trend_name)
    media_url = f"http://example.com/media{random.randint(1, 500)}.jpg"
    hashtags = random.sample(hashtags_pool, k=random.randint(1, 4))
    timestamp = datetime.now() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
    likes = random.randint(5, 500)
    shares = random.randint(1, 100)
    comments = random.randint(0, 50)

    # Trend score calculation
    frequency_score = random.uniform(0.1, 1.0)
    engagement_score = (0.4 * likes + 0.3 * shares + 0.3 * comments) / 500
    recency_score = 1.0 - (datetime.now() - timestamp).days / 60  # decay factor
    trend_score = round(0.5 * frequency_score + 0.4 * engagement_score + 0.1 * recency_score, 2)

    tags = random.sample(tags_pool, k=3)

    # Insert into DB
    cur.execute("""
                INSERT INTO synthetic_fashion_trends
                (content, media_url, hashtags, timestamp, likes, shares, comments, trend_name, trend_type, trend_score,
                 tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (content, media_url, hashtags, timestamp, likes, shares, comments, trend_name, trend_type, trend_score,
                 tags))

# --- Commit and close ---
conn.commit()
cur.close()
conn.close()

print(f"{num_posts} realistic synthetic fashion posts inserted successfully!")
