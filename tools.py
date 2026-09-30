"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


_STOPWORDS = {
    "a", "an", "and", "for", "in", "is", "looking", "of", "on", "or",
    "the", "to", "under", "with",
}


def _keywords(text: str) -> set[str]:
    """Normalize text into searchable keyword tokens."""
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if token not in _STOPWORDS and len(token) > 1
    }


def _size_matches(requested: str, listing_size: str) -> bool:
    """Token-aware size matching that avoids matching clothing sizes inside shoe sizes."""
    requested = requested.strip().lower()
    listing_size_lower = listing_size.lower()

    if not requested:
        return True
    if requested == listing_size_lower.strip():
        return True

    requested_tokens = re.findall(r"[a-z0-9]+", requested)
    listing_tokens = re.findall(r"[a-z0-9]+", listing_size_lower)

    # Shoe sizes should match numeric tokens exactly, e.g. 8 with US 8, not 8.5.
    if any(token.isdigit() for token in requested_tokens):
        return any(token in listing_tokens for token in requested_tokens if token.isdigit())

    clothing_sizes = {"xxs", "xs", "s", "m", "l", "xl", "xxl"}
    requested_clothing = [token for token in requested_tokens if token in clothing_sizes]
    if requested_clothing:
        return any(token in listing_tokens for token in requested_clothing)

    return requested in listing_size_lower


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    listings = load_listings()
    query_terms = _keywords(description)

    matches: list[tuple[int, dict]] = []
    for listing in listings:
        if max_price is not None and float(listing.get("price", 0)) > max_price:
            continue
        if size is not None and not _size_matches(size, str(listing.get("size", ""))):
            continue

        title = listing.get("title", "")
        tags_text = " ".join(listing.get("style_tags", []))
        searchable_parts = [
            title,
            listing.get("description", ""),
            listing.get("category", ""),
            tags_text,
            " ".join(listing.get("colors", [])),
            listing.get("brand") or "",
            listing.get("platform", ""),
        ]
        listing_terms = _keywords(" ".join(searchable_parts))
        score = len(query_terms & listing_terms)

        normalized_description = " ".join(sorted(query_terms))
        title_and_tags = f"{title} {tags_text}".lower()
        if description.lower().strip() in title_and_tags:
            score += 5
        elif normalized_description and normalized_description in title_and_tags:
            score += 3
        score += len(query_terms & _keywords(title))
        score += len(query_terms & _keywords(tags_text))

        if score > 0:
            matches.append((score, listing))

    matches.sort(key=lambda pair: (-pair[0], pair[1].get("price", 0)))
    return [listing for _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    title = new_item.get("title", "this thrift find")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform", "the listing platform")
    tags = ", ".join(new_item.get("style_tags", [])) or "no listed style tags"
    colors = ", ".join(new_item.get("colors", [])) or "unspecified colors"
    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    if not wardrobe_items:
        prompt = f"""
Suggest one or two general outfit ideas for this thrift item. The user has not saved any wardrobe items yet, so do not pretend to know what they own.

Item: {title}
Price: ${price}
Platform: {platform}
Style tags: {tags}
Colors: {colors}

Return a concise, practical styling suggestion.
""".strip()
    else:
        formatted_wardrobe = "\n".join(
            f"- {item.get('name')} ({item.get('category')}; colors: {', '.join(item.get('colors', []))}; tags: {', '.join(item.get('style_tags', []))})"
            for item in wardrobe_items
        )
        prompt = f"""
Suggest one or two outfits using this thrift item and pieces from the user's wardrobe. Name specific wardrobe pieces when they are useful.

New thrift item: {title}
Price: ${price}
Platform: {platform}
Style tags: {tags}
Colors: {colors}

User wardrobe:
{formatted_wardrobe}

Return a concise, practical styling suggestion.
""".strip()

    return generate(
        prompt,
        system="You are a concise personal stylist for thrift shoppers. Be specific and practical.",
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "I need an outfit suggestion before I can write a fit card for this item."

    title = new_item.get("title", "this thrift find")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform", "the listing platform")
    tags = ", ".join(new_item.get("style_tags", [])) or "no listed style tags"
    colors = ", ".join(new_item.get("colors", [])) or "unspecified colors"

    prompt = f"""
Write a short social caption someone would actually post for this thrift find.

Item: {title}
Price: ${price}
Platform: {platform}
Style tags: {tags}
Colors: {colors}
Outfit idea: {outfit}

Requirements:
- 2 to 4 sentences.
- Mention the item once.
- Mention the price once.
- Mention the platform once.
- Sound like a real fit caption, not a product listing.
""".strip()

    return generate(
        prompt,
        system="You write concise, natural thrift outfit captions for social posts.",
    )
