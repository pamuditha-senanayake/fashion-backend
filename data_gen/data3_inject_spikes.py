import psycopg2
import random

# --- Connect to PostgreSQL ---
conn = psycopg2.connect(
    host="localhost",
    database="fashionsite",
    user="pamudithasenanayake",
    password="123"
)
cur = conn.cursor()

# --- Pick some trend names to spike ---
spike_trends = ["bucket hat", "leather boots", "plaid skirt", "sneaker trend"]
num_spikes_per_trend = 3  # how many posts to spike per trend

for trend in spike_trends:
    # Fetch recent posts for this trend
    cur.execute("""
                SELECT id, trend_score
                FROM synthetic_fashion_trends
                WHERE trend_name = %s
                ORDER BY timestamp DESC
                    LIMIT %s
                """, (trend, num_spikes_per_trend))
    rows = cur.fetchall()

    for row in rows:
        post_id = row[0]
        current_score = row[1]
        # Add spike: random jump or drop
        spike = random.uniform(0.2, 0.5) * random.choice([-1, 1])
        new_score = max(0, min(1, current_score + spike))

        # Update the post in DB
        cur.execute("""
                    UPDATE synthetic_fashion_trends
                    SET trend_score = %s
                    WHERE id = %s
                    """, (new_score, post_id))

# --- Commit and close ---
conn.commit()
cur.close()
conn.close()

print(f"Injected spikes into trends: {spike_trends}")
