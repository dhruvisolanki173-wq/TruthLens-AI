
import re
import html
import requests
import xml.etree.ElementTree as ET

from urllib.parse import quote_plus
from django.shortcuts import render


def get_related_news(query):
    """Search Google News RSS for related online reports."""

    url = (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TruthLensAI/1.0)"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=12
    )
    response.raise_for_status()

    root = ET.fromstring(response.content)
    articles = []

    for item in root.findall(".//item")[:8]:
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()

        source_element = item.find("source")

        source = (
            source_element.text.strip()
            if source_element is not None and source_element.text
            else "News source"
        )

        published = item.findtext(
            "pubDate", default=""
        ).strip()

        description = item.findtext(
            "description", default=""
        ).strip()

        description = re.sub(r"<[^>]+>", " ", description)
        description = html.unescape(description)
        description = " ".join(description.split())

        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "source": source,
                "published": published,
                "description": description,
            })

    return articles


def get_keywords(text):
    """Extract meaningful words from text."""

    stop_words = {
        "the", "and", "for", "that", "this", "with", "from",
        "was", "were", "are", "is", "has", "have", "had",
        "will", "would", "could", "should", "about", "after",
        "before", "into", "over", "under", "their", "they",
        "them", "then", "than", "its", "his", "her", "who",
        "what", "when", "where", "why", "how", "not", "but",
        "all", "any", "you", "your", "our", "out", "new",
        "can", "may", "been", "being", "also", "says", "said",
    }

    words = re.findall(r"[a-zA-Z0-9]+", text.lower())

    return {
        word for word in words
        if len(word) > 2 and word not in stop_words
    }


def analyze_evidence(news, articles):
    """
    Compare a claim with online reports.

    The score measures keyword overlap, not the probability
    that the claim is true or false.
    """

    input_keywords = get_keywords(news)

    if not articles:
        return {
            "verdict": "Unverified",
            "confidence": 0,
            "confidence_label": "Search Match Score",
            "explanation": (
                "No related reports were found. More evidence is "
                "needed before this claim can be assessed."
            ),
        }

    scored_articles = []

    debunk_phrases = [
        "fact check",
        "fact-check",
        "debunked",
        "false claim",
        "claim is false",
        "not true",
        "no evidence",
        "misleading claim",
        "fake news",
        "hoax",
        "did not happen",
        "not happening",
    ]

    confirmation_phrases = [
        "fact check confirms",
        "claim is true",
        "claim is accurate",
        "verified claim",
    ]

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")

        article_text = f"{title} {description}".lower()
        article_keywords = get_keywords(article_text)
        overlap = input_keywords & article_keywords

        score = (
            len(overlap) / len(input_keywords) * 100
            if input_keywords
            else 0
        )

        is_debunk = any(
            phrase in article_text
            for phrase in debunk_phrases
        )

        is_confirmed = any(
            phrase in article_text
            for phrase in confirmation_phrases
        )

        scored_articles.append({
            **article,
            "score": score,
            "matched_keywords": sorted(overlap),
            "is_debunk": is_debunk,
            "is_confirmed": is_confirmed,
        })

    scored_articles.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    best = scored_articles[0]
    match_score = round(best["score"], 1)

    # Only consider reports with sufficient keyword overlap.
    relevant_reports = [
        article
        for article in scored_articles
        if article["score"] >= 30
    ]

    debunk_reports = [
        article
        for article in relevant_reports
        if article["is_debunk"]
    ]

    confirmation_reports = [
        article
        for article in relevant_reports
        if article["is_confirmed"]
    ]

    if (
        len(debunk_reports) >= 2
        and len(confirmation_reports) == 0
    ):
        verdict = "Possible False Claim"

        explanation = (
            "Multiple search results contain wording commonly "
            "associated with debunking or fact-checking. Open the "
            "reports and confirm that they address the exact claim. "
            "This automated analysis is not a definitive verdict."
        )

    elif (
        len(confirmation_reports) >= 2
        and len(debunk_reports) == 0
    ):
        verdict = "Possible Supported Claim"

        explanation = (
            "Multiple search results contain wording suggesting "
            "confirmation. Check the original sources to determine "
            "whether they actually support the exact claim."
        )

    else:
        verdict = "Unverified"

        matched = best["matched_keywords"]

        explanation = (
            f'The closest matching report is "{best["title"]}" '
            f'from {best["source"]}. '
            f'Matching keywords include: '
            f'{", ".join(matched[:10]) if matched else "none"}. '
            "The available search results do not provide enough "
            "unambiguous evidence to classify the claim as true "
            "or false. Read the linked reports for their conclusions."
        )

    return {
        "verdict": verdict,
        "confidence": match_score,
        "confidence_label": "Search Match Score",
        "explanation": explanation,
    }


def home(request):
    return render(request, "home.html")


def check_news(request):
    news = ""
    articles = []
    result = None
    error = None

    if request.method == "POST":
        news = request.POST.get("news", "").strip()

        if not news:
            error = "Please enter a news headline or claim."

        elif len(news) > 2000:
            error = (
                "Please enter text shorter than 2,000 characters."
            )

        else:
            try:
                articles = get_related_news(news)
                result = analyze_evidence(news, articles)

            except requests.RequestException:
                error = (
                    "Online news search is temporarily unavailable. "
                    "Check your internet connection and try again."
                )

            except ET.ParseError:
                error = (
                    "The news search returned an unreadable response. "
                    "Please try again."
                )

    return render(
        request,
        "check_news.html",
        {
            "news": news,
            "articles": articles,
            "result": result,
            "error": error,
        },
    )
