
from pathlib import Path

import joblib


# Find the saved model relative to this file
MODEL_PATH = Path(__file__).with_name("fake_news_model.pkl")

model = joblib.load(MODEL_PATH)


def predict_news(news_text):
    news_text = news_text.strip()

    if not news_text:
        return {
            "prediction": "No news entered",
            "confidence": None
        }

    prediction = model.predict([news_text])[0]
    probabilities = model.predict_proba([news_text])[0]
    confidence = round(float(max(probabilities)) * 100, 2)

    return {
        "prediction": prediction,
        "confidence": confidence
    }


if __name__ == "__main__":
    sample_news = input("Enter a news headline: ")

    result = predict_news(sample_news)

    print("Prediction:", result["prediction"])
    print("Model confidence:", result["confidence"], "%")
    print("Note: This tiny demonstration model is not reliable for real news.")
