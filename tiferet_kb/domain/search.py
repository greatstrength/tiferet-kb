"""tiferet_kb Search Domain"""

# *** imports

# ** core
from typing import Dict, List

# *** constants

# ** constant: rrf_k
RRF_K = 60

# *** functions

# ** function: tokenize
def tokenize(text: str) -> List[str]:
    '''
    Split text into casefolded alphanumeric tokens.

    A token is a maximal run of characters for which ``str.isalnum`` is
    true, then ``str.casefold``. Underscore, hyphen, and markdown
    punctuation are separators. The same split is used on a rendered body
    and on a query.

    :param text: The string to tokenize.
    :type text: str
    :return: Tokens in encounter order, duplicates included.
    :rtype: List[str]
    '''

    # A non-string has no tokens. Do not raise.
    if not isinstance(text, str) or not text:
        return []

    # Walk the string once. Flush a run when a separator is seen.
    tokens: List[str] = []
    buf: List[str] = []
    for char in text:
        if char.isalnum():
            buf.append(char)
            continue
        if buf:
            tokens.append(''.join(buf).casefold())
            buf = []

    # Flush a token that runs to the end of the string.
    if buf:
        tokens.append(''.join(buf).casefold())
    return tokens

# ** function: query_tokens
def query_tokens(text: str) -> List[str]:
    '''
    Return the distinct tokens of a query, in first-seen order.

    ``alpha alpha`` is the query ``alpha``. Order does not affect the score.

    :param text: The query string.
    :type text: str
    :return: Distinct tokens.
    :rtype: List[str]
    '''

    # Keep the first occurrence. Later repeats add nothing.
    seen = set()
    distinct: List[str] = []
    for token in tokenize(text):
        if token in seen:
            continue
        seen.add(token)
        distinct.append(token)
    return distinct

# ** function: fuse_rankings
def fuse_rankings(keyword_hits: List[Dict], embedding_hits: List[Dict]) -> List[Dict]:
    '''
    Merge two already-ranked hit lists with reciprocal rank fusion.

    Rank is the 1-based position in the list as given. A section on one
    side keeps that side's term. The score is the fusion sum, never a
    BM25 score and never a cosine.

    :param keyword_hits: Keyword hits, best rank first.
    :type keyword_hits: List[Dict]
    :param embedding_hits: Embedding hits, best rank first.
    :type embedding_hits: List[Dict]
    :return: Fused hits, score descending, then section_id ascending.
    :rtype: List[Dict]
    '''

    # Add each side's reciprocal rank. A missing side contributes nothing.
    scores: Dict[str, float] = {}
    for rank, hit in enumerate(keyword_hits, start=1):
        section_id = hit['section_id']
        scores[section_id] = scores.get(section_id, 0.0) + 1.0 / (RRF_K + rank)
    for rank, hit in enumerate(embedding_hits, start=1):
        section_id = hit['section_id']
        scores[section_id] = scores.get(section_id, 0.0) + 1.0 / (RRF_K + rank)

    # Sort the fusion scores. Equal scores do not share a rank.
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [
        {'section_id': section_id, 'score': float(score)}
        for section_id, score in ranked
    ]

# ** function: sort_hits
def sort_hits(hits: List[Dict]) -> List[Dict]:
    '''
    Order hits by score descending, then section_id ascending.

    Equal scores do not share a rank. The lower section_id is the better rank.

    :param hits: Hits with section_id and score.
    :type hits: List[Dict]
    :return: The same hits, ranked.
    :rtype: List[Dict]
    '''

    # Break ties in the key. Do not leave equal scores in encounter order.
    return sorted(hits, key=lambda hit: (-hit['score'], hit['section_id']))

# ** function: cut_hits
def cut_hits(hits: List[Dict], limit: int) -> List[Dict]:
    '''
    Apply a result limit after ranking.

    A limit less than 1 returns an empty list and does not raise. A limit
    past the end returns every hit.

    :param hits: Ranked hits.
    :type hits: List[Dict]
    :param limit: Maximum number of hits to keep.
    :type limit: int
    :return: The prefix of hits, or an empty list.
    :rtype: List[Dict]
    '''

    # A non-positive limit is an empty result, not an error.
    if limit < 1:
        return []

    # Slice after the ranking. Do not rank again.
    return hits[:limit]
