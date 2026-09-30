# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 because the search will use simple parsing and keyword overlap, so one reasonable phrasing may miss even when the data has a related item. A matching query should usually complete, but I do not expect plain keyword search to understand every synonym.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
I picked 5 of 5 because this path is deterministic after search: an empty list should always trigger the same branch. Unlike model-generated captions, stopping before the second tool should not vary from run to run.

---

## 3. The selected listing is preserved in session state

Given a matching query, the listing stored in `session["selected_item"]` has the same `id` and `title` as the first listing in `session["search_results"]`, and the outfit suggestion refers to that same selected item — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 because the session copy should always preserve the exact listing, but the model-written outfit text may sometimes describe the item without repeating its exact title. Checking both the stored `id`/`title` and the outfit wording gives evidence that state flowed through the loop without requiring perfect model wording every time.

---

## 4. The fit card includes the details needed to post it

Given a matching query, the returned fit card is two to four sentences long and mentions the selected item's price and platform — in at least 4 of 5 tries.

**Why this target:**
I picked 4 of 5 because the fit card is model-generated, so wording can vary, but price and platform are concrete details from the listing that should usually survive the prompt. I did not choose 5 of 5 because a caption may occasionally be good but omit one required detail, which is exactly the kind of variation I want to measure next unit.

---

## 5. Search respects the user's price ceiling

Given a query with a maximum price, every listing in `session["search_results"]` has `price <= session["parsed"]["max_price"]` — 5 of 5 tries.

**Why this target:**
I picked 5 of 5 because price filtering is deterministic and does not depend on model output. If the user asks for an item under a budget, returning a listing above that budget is a clear tool failure, not acceptable variation.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
