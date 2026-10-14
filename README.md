# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps a user search thrift listings from a plain-language request like "vintage graphic tee under $30." It finds matching listings, picks one item, suggests how to wear it with the user's saved wardrobe, and writes a short fit-card caption. If nothing matches, it stops before outfit generation and tells the user what they could change, such as price, size, or description.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the local listings data for thrift items matching the user's description, optional size, and optional maximum price.
- **Inputs:** `description` (`str`), `size` (`str | None`), `max_price` (`float | None`). Size matching should be case-insensitive and token-aware, so `M` can match `S/M` or `M/L` but `S` does not match `US 9`.
- **Returns:** A list of listing dictionaries, best match first, with each dict containing `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.
- **When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

- **What it does:** Suggests one or two ways to style the selected thrift item with the user's wardrobe.
- **Inputs:** `new_item` (`dict` listing with the fields returned by `search_listings`), `wardrobe` (`dict` with an `items` list of wardrobe item dicts).
- **Returns:** A non-empty string with outfit ideas that name the selected item and, when wardrobe items exist, specific pieces from the user's wardrobe.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns a non-empty string with general styling advice for the item instead of failing.

### `create_fit_card`

- **What it does:** Writes a short social caption for the selected item and outfit idea.
- **Inputs:** `outfit` (`str`), `new_item` (`dict` listing with title, price, platform, and style details).
- **Returns:** A two-to-four sentence string that reads like a post caption and mentions the item, price, platform, and outfit vibe.
- **When it has nothing:** If `outfit` is empty or whitespace, returns a short message explaining that a fit card cannot be created without an outfit suggestion.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a useful message in `session["error"]` naming what the user could change and stop without calling `suggest_outfit` or `create_fit_card`. Otherwise, take the first listing, store it in `session["selected_item"]`, pass it to `suggest_outfit`, then pass the resulting outfit suggestion and same selected item to `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex/string parsing: extract a price from phrases like `under $30`, extract a size from phrases like `size M` or `in size M`, and use the remaining words as the description.

**What moves through the session:** The original query goes into `session["query"]`; parsed `description`, `size`, and `max_price` go into `session["parsed"]`; search results go into `session["search_results"]`; the first result goes into `session["selected_item"]`; the outfit text goes into `session["outfit_suggestion"]`; the final caption goes into `session["fit_card"]`; early-stop messages go into `session["error"]`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ .venv/bin/python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear**
*   **Bottoms:** Baggy straight-leg jeans
*   **Outerwear:** Black cropped zip hoodie (worn open)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* Balances the fitted baby tee with baggy denim, nailing the Y2K streetwear proportion.

**Outfit 2: High-Low Contrast**
*   **Bottoms:** Wide-leg khaki trousers secured with the brown leather belt
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Black combat boots
*   *Why it works:* Combines the girly, pastel butterfly print with edgy boots and structured earth-tone trousers for an easy contrast.

  Fit card: Scored this butterfly print Y2K baby tee for just $18 on Depop and I’m obsessed. Already styling it with baggy denim and chunky sneakers for the ultimate off-duty look. Grab it before I change my mind!

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ .venv/bin/python -c "from tools import search_listings; print([(x['id'], x['title'], x['price'], x['size']) for x in search_listings('graphic tee', max_price=30)])"
[('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0, 'L'), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0, 'L'), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0, 'W29')]
```

```
$ .venv/bin/python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[5], get_example_wardrobe()))"
**Outfit 1: 90s Streetwear**
*   **Bottoms:** Baggy dark-wash straight-leg jeans
*   **Outerwear:** Vintage black denim jacket (worn open)
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag
*   *Why it works:* Double black denim grounds the graphic tee, while the chunky sneakers and baggy fit lean straight into the 2003 bootleg aesthetic.

**Outfit 2: High-Low Grunge**
*   **Bottoms:** Wide-leg khaki trousers
*   **Layering (Inner):** White ribbed tank top (let the hem peek out under the tee)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt, black crossbody bag
*   *Why it works:* Tucking the tee into khaki trousers adds structure, and the combat boots pull the look toward effortless grunge.
```

```
$ .venv/bin/python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('Pair it with baggy dark-wash jeans and chunky white sneakers.', load_listings()[5]))"
Scored this 2003 tour graphic tee and I'm obsessed with the faded wash. It’s giving major grunge energy and looks so good with baggy denim. Grabbed it on Depop for just $24.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked the coding agent to inspect the starter repo and create a phase-by-phase plan without writing code.
- *What came back:* It identified that `tools.py`, `agent.py`, `README.md`, and `criteria.md` were still stubs, confirmed the venv command needed to be `.venv/bin/python`, and proposed separate phases for specs, tools, loop wiring, and writeup.
- *What I changed:* I approved the phases one at a time, starting with the documentation/spec phase before any implementation so the criteria existed before the results.

**Moment 2**

- *What I asked for:* I approved implementation of the three tools after the specs were written.
- *What came back:* The agent implemented keyword search, token-aware size matching, model prompts for outfit suggestions, and a fit-card prompt.
- *What I changed:* After the first search test ranked some loose matches above the direct graphic tee result, the search scoring was adjusted to give extra weight to title and style-tag matches.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before tool 2 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected listing is preserved in session | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card includes posting details | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search respects the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

The complete unedited output is in
`results/run_2026-10-14_1518_before.md`, produced by
`run_eval.py::main` from sessions returned by `agent.py::run_agent`. Caching
was off, and the run made 40 model calls. These are real excerpts from one try
for each criterion:

**Criterion 1 — Try 1**

```text
stopped early: no
selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
search_results: 10

Outfit suggestion:
**Y2K Streetwear Look**
* Bottoms: Baggy dark-wash straight-leg jeans
* Shoes: Chunky white sneakers
* Outerwear: Black cropped zip hoodie (worn open)
* Accessories: Black crossbody bag

Fit card:
Finally secured the ultimate butterfly baby tee for just $18 on Depop. Paired
it with baggy denim and a zip hoodie for the exact proportion I’ve been hunting
for. Grab it before I change my mind and keep it.

Trace tools: search_listings (via MCP) -> suggest_outfit -> create_fit_card
```

**Criterion 2 — Try 1**

```text
stopped early: yes — I couldn't find matching listings. Try changing the item
description, choosing a different size, or raising the max price.
selected_item: (none)
search_results: 0
trace: search_listings (via MCP) returned [] (empty) -> branch: empty, stopping
```

**Criterion 3 — Try 1**

```text
first search result: lst_007 | Denim Jacket — Light Wash, Cropped
selected item: lst_007 | Denim Jacket — Light Wash, Cropped
outfit suggestion:
**Look 1: Double Denim Streetwear**
* Base: White ribbed tank top + Baggy dark-wash straight-leg jeans with the
  brown leather belt.
* Outerwear: Cropped light-wash denim jacket (creates a trendy high-contrast
  Canadian tuxedo).
* Shoes & Accessories: Chunky white sneakers + Black crossbody bag.
```

The report's five traces show `select_listing` taking the first search result.
The exact `id`/`title` output above came from a supporting call to
`agent.py::run_agent` after the baseline report and confirms that the two
session records match as well as the displayed titles.

**Criterion 4 — Try 1**

```text
Found this dreamy butterfly baby tee and I'm obsessed. Snagged it on Depop for
just $18. Throwing it on with baggy denim and sneakers for the ultimate 2000s
street look.
```

This is three sentences and includes both `$18` and `Depop`.

**Criterion 5 — Try 1**

```text
parsed: {'description': 'graphic tee', 'size': None, 'max_price': 20.0}
result prices: [18.0, 19.0, 15.0]
```

The parsed value came from `agent.py::_parse_query`; the prices came from
`mcp_client.call_tool("search_listings", parsed)`. The MCP search is
deterministic, and all five traces returned the same three listings.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | **MET (5/5)** | Every trace contains the MCP search, outfit tool, and fit-card tool in order, and every run returned a non-empty fit card. |
| 2 | Impossible query stops before tool 2 | 5 of 5 | **MET (5/5)** | Every MCP search returned `[]`; each trace stopped after the search and each error named description, size, or price as something to change. |
| 3 | Selected listing is preserved in session | 4 of 5 | **MET (5/5)** | In every run the first result and selected item were the light-wash cropped denim jacket, and every outfit explicitly styled that jacket. |
| 4 | Fit card includes posting details | 4 of 5 | **MET (5/5)** | All five cards had three sentences and included the selected item's `$18` price and `Depop` platform. |
| 5 | Search respects the price ceiling | 5 of 5 | **MET (5/5)** | Every run parsed a `$20` maximum and returned prices `[18.0, 19.0, 15.0]`; none exceeded the limit. |

**Diagnoses**

No criterion missed, so there is no miss to attribute to a tool, branch,
session, or model output. The two deterministic behaviors—the empty branch
and price filter—were stable at 5/5. The three model-involving criteria also
met their 4/5 targets, although those targets only exercised one query each,
so the result demonstrates consistency more than broad item coverage.

One quality problem appeared outside the five criteria: criterion 3's third
fit card invented `Shop my Poshmark closet: [Insert Closet Link]`. The
mechanism is in the `create_fit_card` model prompt: it asks for a social post
but does not forbid invented links, calls to action, or facts absent from the
listing. This did not make criterion 3 fail because that criterion measures
session identity and outfit continuity, not unsupported fit-card content.
It is the clearest candidate for the one improvement.

If I tightened a criterion in a future test, I would run the model-related
criteria across five different matching items rather than five repetitions of
one item, and I would explicitly check that captions contain no invented URLs
or unsupported seller claims. I did not revise `criteria.md` because the
original criteria were measurable and were applied as written.


---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

Command: `.venv/bin/python app.py ask 'vintage graphic tee under $30' --trace`

```text
[1] parse_query
      in:  vintage graphic tee under $30
      out: description='vintage graphic tee', size=None, max_price=30.0
[2] search_listings (via MCP)
      in:  description='vintage graphic tee', size=None, max_price=30.0
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    branch: continue
[3] select_listing
      in:  first search result
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  item='Y2K Baby Tee — Butterfly Print', wardrobe_items=10
      out: **Outfit 1: Y2K Streetwear** *   **Bottoms:** Baggy straight-leg jeans *   **Outerwear:** Black cropped zip ho…
[5] create_fit_card
      in:  outfit='**Outfit 1: Y2K Streetwear**\n*   **Bottoms:** Baggy straight-leg jeans\n*   **Outerwear:** Black crop…
      out: Scored this butterfly print Y2K baby tee for just $18 on Depop and I’m obsessed. Already styling it with baggy…
```

**Empty search**

Command: `.venv/bin/python app.py ask 'designer ballgown size XXS under $5' --trace`

```text
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: description='designer ballgown', size='XXS', max_price=5.0
[2] search_listings (via MCP)
      in:  description='designer ballgown', size='XXS', max_price=5.0
      out: [] (empty)
      →    branch: empty, stopping
```

The shorter empty-search trace confirms that `suggest_outfit` and
`create_fit_card` were not called after the MCP tool returned an empty list.

**Deliberate failure checks**

- **Empty search:** `I couldn't find matching listings. Try changing the item description, choosing a different size, or raising the max price.`
- **Empty wardrobe:** Running `denim jacket under $50 --empty-wardrobe` returned general advice rather than crashing or returning an empty string. It named the problem and gave the user a next action without claiming the suggested pieces were saved:

  ```text
  Your saved wardrobe is empty, so these are general styling ideas. Add wardrobe pieces for personalized combinations.

  1. Model-Off-Duty Streetwear
  - Bottoms: High-waisted black wide-leg cargo pants.
  - Top: Fitted ribbed white tank top.
  - Footwear: Retro white leather sneakers (like Adidas Sambas).
  - Accessory: A black nylon shoulder bag.

  2. Casual Weekend Classic
  - Bottoms: Olive green or beige utility midi skirt.
  - Top: Oversized graphic tee (tucked in).
  - Footwear: Canvas slip-on sneakers or chunky loafers with white socks.
  - Accessory: A canvas tote bag.
  ```
- **Model unavailable:** After changing one character of the API key and using a new uncached query, the agent returned: `The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.` The original key was restored immediately afterward.

All three messages give the user a next action: broaden the search, use general
styling advice or save wardrobe pieces, and check or replace the API key.

**On the MCP move:** `mcp_server.py` now publishes `search_listings` with typed
inputs, and `agent.py::run_agent` calls it through `mcp_client.call_tool`
instead of importing it directly. Comparing direct and MCP calls produced the
same list of dictionaries for a matching query and the same empty list for an
impossible query, so behavior did not change after the rewire.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
