# -*- coding: utf-8 -*-
"""
Publica en X (Twitter) usando la API gratuita.
"""
from pathlib import Path
from typing import Optional

import tweepy

from config import (
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
)


def publicar_x(texto: str, ruta_imagen: Optional[Path] = None) -> bool:
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        return False
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )
        api_v1 = tweepy.API(
            tweepy.OAuth1UserHandler(
                TWITTER_API_KEY,
                TWITTER_API_SECRET,
                TWITTER_ACCESS_TOKEN,
                TWITTER_ACCESS_TOKEN_SECRET,
            )
        )
        if ruta_imagen and Path(ruta_imagen).exists():
            media = api_v1.media_upload(filename=str(ruta_imagen))
            client.create_tweet(text=texto[:280], media_ids=[media.media_id])
        else:
            client.create_tweet(text=texto[:280])
        return True
    except Exception:
        return False
