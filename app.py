from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from recommendation_model import RecommendationSystem
from database import init_db, add_to_cart, get_cart, clear_cart
import os

app = Flask(__name__)

# Preprocess data if not already done
if not os.path.exists("data/processed_clothing_data.csv"):
    df = pd.read_csv("data/Womens Clothing E-Commerce Reviews.csv")
    df['user_id'] = ['user_' + str(i % 1000) for i in range(len(df))]
    processed_df = df[['Clothing ID', 'Department Name', 'Title', 'Review Text', 'Rating', 'user_id']].copy()
    processed_df.columns = ['Clothing ID', 'Category', 'Title', 'Description', 'Rating', 'user_id']
    processed_df['Price'] = [f"${(i % 50 + 10):.2f}" for i in range(len(processed_df))]
    processed_df['Description'] = processed_df['Description'].fillna('No description available')
    processed_df['Title'] = processed_df['Title'].fillna('Untitled')
    processed_df['Category'] = processed_df['Category'].fillna('Unknown')
    processed_df = processed_df.dropna(subset=['Clothing ID', 'Rating', 'user_id'])
    processed_df.to_csv("data/processed_clothing_data.csv", index=False)

# Load processed data
df = pd.read_csv("data/processed_clothing_data.csv")
ratings = df[['user_id', 'Clothing ID', 'Rating']]

# Calculate average ratings per Clothing ID
avg_ratings = ratings.groupby('Clothing ID')['Rating'].mean().reset_index()
avg_ratings.columns = ['Clothing ID', 'Avg Rating']

# Merge with product details
products = df.drop_duplicates(subset=['Clothing ID'])[['Clothing ID', 'Category', 'Title', 'Description', 'Price']]
products = products.merge(avg_ratings, on='Clothing ID', how='left')

# Get unique categories
categories = products['Category'].unique().tolist()

recommender = RecommendationSystem()
recommender.prepare_data(ratings)
recommender.train_model()

# Initialize SQLite database for cart
init_db()

@app.route('/')
def home():
    cart_items = get_cart()
    category_filter = request.args.get('category', 'All')
    rating_filter = request.args.get('rating', 'All')
    
    filtered_products = products.copy()
    if category_filter != 'All':
        filtered_products = filtered_products[filtered_products['Category'] == category_filter]
    if rating_filter != 'All':
        min_rating = float(rating_filter.split('+')[0])
        filtered_products = filtered_products[filtered_products['Avg Rating'] >= min_rating]
    
    return render_template('index.html', 
                           products=filtered_products.to_dict('records'), 
                           cart_items=cart_items, 
                           categories=categories, 
                           selected_category=category_filter, 
                           selected_rating=rating_filter)

@app.route('/rate', methods=['POST'])
def rate_product():
    user_id = request.form['user_id']
    clothing_id = request.form['clothing_id']
    rating = int(request.form['rating'])
    
    global ratings, products, recommender
    new_rating = pd.DataFrame([[user_id, clothing_id, rating]], columns=['user_id', 'Clothing ID', 'Rating'])
    ratings = pd.concat([ratings, new_rating]).drop_duplicates(subset=['user_id', 'Clothing ID'], keep='last')
    avg_ratings = ratings.groupby('Clothing ID')['Rating'].mean().reset_index()
    avg_ratings.columns = ['Clothing ID', 'Avg Rating']
    products = products.drop(columns=['Avg Rating']).merge(avg_ratings, on='Clothing ID', how='left')
    recommender.prepare_data(ratings)
    recommender.train_model()
    return jsonify({'status': 'success'})

@app.route('/update_rating', methods=['POST'])
def update_rating():
    user_id = request.form['user_id']
    clothing_id = request.form['clothing_id']
    rating = int(request.form['rating'])
    
    global ratings, products, recommender
    ratings.loc[(ratings['user_id'] == user_id) & (ratings['Clothing ID'] == clothing_id), 'Rating'] = rating
    avg_ratings = ratings.groupby('Clothing ID')['Rating'].mean().reset_index()
    avg_ratings.columns = ['Clothing ID', 'Avg Rating']
    products = products.drop(columns=['Avg Rating']).merge(avg_ratings, on='Clothing ID', how='left')
    recommender.prepare_data(ratings)
    recommender.train_model()
    return jsonify({'status': 'success'})

@app.route('/delete_rating', methods=['POST'])
def delete_rating():
    user_id = request.form['user_id']
    clothing_id = request.form['clothing_id']
    
    global ratings, products, recommender
    ratings = ratings[~((ratings['user_id'] == user_id) & (ratings['Clothing ID'] == clothing_id))]
    avg_ratings = ratings.groupby('Clothing ID')['Rating'].mean().reset_index()
    avg_ratings.columns = ['Clothing ID', 'Avg Rating']
    products = products.drop(columns=['Avg Rating']).merge(avg_ratings, on='Clothing ID', how='left')
    recommender.prepare_data(ratings)
    recommender.train_model()
    return jsonify({'status': 'success'})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    clothing_id = request.form['clothing_id']
    add_to_cart(clothing_id)
    return jsonify({'status': 'success', 'cart': get_cart()})

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = request.form.get('user_id', 'guest')
    cart_items = get_cart()
    if not cart_items:
        return render_template('recommendations.html', recommendations=[], message="Add items to your cart to get recommendations!")
    
    cart_df = pd.DataFrame({'user_id': [user_id]*len(cart_items), 'Clothing ID': cart_items, 'Rating': [5]*len(cart_items)})
    extended_ratings = pd.concat([ratings, cart_df]).drop_duplicates(subset=['user_id', 'Clothing ID'], keep='last')
    recommender.prepare_data(extended_ratings)
    recommendations = recommender.get_recommendations(user_id, n=5)
    
    actual_ratings = ratings[ratings['user_id'] == user_id]['Clothing ID'].tolist()
    recommended_ids = [item[0] for item in recommendations]
    precision = len(set(recommended_ids) & set(actual_ratings)) / 5 if actual_ratings else 0
    clear_cart()
    return render_template('recommendations.html', recommendations=recommendations, precision=precision)

if __name__ == "__main__":
    app.run(debug=True)