from flask import Flask, render_template, request, jsonify
import pandas as pd
from recommendation_model import RecommendationSystem
from database import init_db, add_to_cart, get_cart, clear_cart

app = Flask(__name__)

# Load data and initialize recommendation system
df = pd.read_csv("data/processed_data.csv")
recommender = RecommendationSystem()
recommender.prepare_data(df)
recommender.train_model()

# Initialize SQLite database
init_db()

@app.route('/')
def home():
    products = df['Clothing ID'].unique().tolist()
    cart_items = get_cart()
    return render_template('index.html', products=products, cart_items=cart_items)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    clothing_id = request.form['clothing_id']
    add_to_cart(clothing_id)
    return jsonify({'status': 'success', 'cart': get_cart()})

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.form.get('user_id', 'guest')  # Default to 'guest' if no user_id
    cart_items = get_cart()
    if not cart_items:
        return render_template('recommendations.html', recommendations=[], message="Add items to your cart to get recommendations!")
    
    # Simulate user ratings from cart (assume rating 5 for cart items)
    cart_df = pd.DataFrame({'user_id': [user_id]*len(cart_items), 'Clothing ID': cart_items, 'Rating': [5]*len(cart_items)})
    extended_df = pd.concat([df, cart_df]).drop_duplicates()
    recommender.prepare_data(extended_df)  # Re-prepare with cart data
    recommendations = recommender.get_recommendations(user_id, n=5)
    clear_cart()  # Optional: Clear cart after recommending
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)