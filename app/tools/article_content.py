from trafilatura import extract, fetch_url


DEFAULT_MAX_CONTENT_CHARS = 6000
MIN_CONTENT_CHARS = 200


def fetch_article_content(
    url: str,
    max_chars: int = DEFAULT_MAX_CONTENT_CHARS,
) -> str | None:
    if not url:
        return None

    if max_chars <= 0:
        raise ValueError(
            "max_chars must be greater than zero."
        )

    try:
        downloaded = fetch_url(url)

        if not downloaded:
            return None

        content = extract(
            downloaded,
            url=url,
            include_comments=False,
            include_tables=False,
        )

        if not content:
            return None

        content = content.strip()

        if len(content) < MIN_CONTENT_CHARS:
            return None

        if len(content) > max_chars:
            content = content[:max_chars].rstrip()

        return content

    except Exception:
        return None