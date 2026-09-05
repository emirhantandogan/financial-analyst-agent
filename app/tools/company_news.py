from datetime import datetime, timedelta, timezone

from ddgs import DDGS


MAX_SEARCH_RESULTS = 20
MAX_RETURNED_RESULTS = 10


def _parse_published_at(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized_value = value.replace("Z", "+00:00")

    try:
        published_at = datetime.fromisoformat(normalized_value)
    except ValueError:
        return None

    if published_at.tzinfo is None:
        published_at = published_at.replace(
            tzinfo=timezone.utc
        )

    return published_at.astimezone(timezone.utc)


def _get_search_timelimit(hours_back: int) -> str | None:
    if hours_back <= 24:
        return "d"

    if hours_back <= 24 * 7:
        return "w"

    if hours_back <= 24 * 31:
        return "m"

    return None


def fetch_company_news(
        ticker: str,
        hours_back: int = 24,
    ) -> list[dict]:
    normalized_ticker = ticker.strip().upper()

    if not normalized_ticker:
        raise ValueError(
            "Ticker cannot be empty."
        )

    if hours_back <= 0:
        raise ValueError(
            "hours_back must be greater than zero."
        )

    cutoff_time = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours_back)
    )

    timelimit = _get_search_timelimit(
        hours_back
    )

    query = f"{normalized_ticker} stock"

    try:
        results = DDGS().news(
            query=query,
            region="us-en",
            safesearch="moderate",
            timelimit=timelimit,
            max_results=MAX_SEARCH_RESULTS,
            backend="auto",
        )

    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch news for "
            f"{normalized_ticker}: {exc}"
        ) from exc

    articles = []

    for result in results:
        published_at = _parse_published_at(
            result.get("date")
        )

        if published_at is None:
            continue

        if published_at < cutoff_time:
            continue

        article = {
            "ticker": normalized_ticker,
            "title": result.get("title"),
            "summary": result.get("body"),
            "source": result.get("source"),
            "url": result.get("url"),
            "published_at": published_at.isoformat(),
        }

        articles.append(article)

    articles.sort(
        key=lambda article: article["published_at"],
        reverse=True,
    )

    return articles[:MAX_RETURNED_RESULTS]