from __future__ import annotations

from typing import cast

import pandas as pd
import requests
from bs4 import BeautifulSoup


def add_html_content(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def _download(row: pd.Series) -> str:
        arxiv_id = row.get("arxiv_id", "")
        if not arxiv_id:
            return ""
        url = f"https://arxiv.org/abs/{arxiv_id}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            html_text: str = resp.text
            return html_text
        except requests.RequestException:
            return ""

    df["html_content"] = df.apply(_download, axis=1)
    df["html_content"] = df["html_content"].astype("string")
    return df


def add_text_from_html(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def _extract(row: pd.Series) -> str:
        html = row.get("html_content", "")
        if not html:
            return ""

        soup = BeautifulSoup(str(html), "html.parser")

        for tag_name in ("script", "style", "nav", "header", "footer"):
            for tag in soup.find_all(tag_name):
                tag.decompose()

        raw_text = soup.get_text(separator=" ", strip=True)
        text_str: str = cast(str, raw_text)
        return text_str

    df["text_content"] = df.apply(_extract, axis=1)
    df["text_content"] = df["text_content"].astype("string")
    return df
