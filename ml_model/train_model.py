
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from dataset import df

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from dataset import df


# Prepare the news text and labels
X = df["text"]
y = df["label"]

# Create a machine learning pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train the model on the sample dataset
model.fit(X, y)

print("Model training completed successfully!")
print("Training examples:", len(X))
print("Labels learned:", sorted(y.unique()))


joblib.dump(model, "fake_news_model.pkl")

print("Model saved successfully!")
