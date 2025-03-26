import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD

class RecommendationSystem:
    def __init__(self, n_components=20):
        self.model = TruncatedSVD(n_components=n_components, random_state=42)
        self.user_item_matrix = None
        self.user_ids = None
        self.item_ids = None
        self.predicted_ratings = None

    def prepare_data(self, df):
        self.user_item_matrix = df.pivot_table(index='user_id', columns='Clothing ID', values='Rating', fill_value=0)
        self.user_ids = self.user_item_matrix.index
        self.item_ids = self.user_item_matrix.columns

    def train_model(self):
        user_features = self.model.fit_transform(self.user_item_matrix)
        item_features = self.model.components_.T
        self.predicted_ratings = pd.DataFrame(np.dot(user_features, item_features.T), index=self.user_ids, columns=self.item_ids)

    def get_recommendations(self, user_id, n=5):
        if self.predicted_ratings is None:
            raise ValueError("Model has not been trained yet!")
        if user_id not in self.user_ids:
            user_ratings = pd.Series(0, index=self.item_ids)  # Default for new user
        else:
            user_ratings = self.predicted_ratings.loc[user_id]
        already_rated = self.user_item_matrix.loc[user_id][self.user_item_matrix.loc[user_id] > 0].index
        recommendations = user_ratings.drop(already_rated).sort_values(ascending=False).head(n)
        return [(item_id, rating) for item_id, rating in recommendations.items()]