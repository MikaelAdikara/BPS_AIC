# Deciqo v5.1 — presenter script (158 s, the video plays silent behind you)

Read it as one story, not a list of features. The timestamps are cues: start that line when the scene
changes, and if you're a beat behind, let the next pause absorb it. Roughly 140 words a minute.
*Italic lines* are safe to drop if you're running long.

---

**0:00** · *review storm, Qo catches one card*

> Every day, a seller gets buried under reviews like these. So instead of showing you all of them,
> let's follow just one. It's four stars. At a glance, it looks perfectly fine.

**0:08** · *01 System — the whole deployment lights up*

> This is Deciqo, the whole system, end to end. Our app, a demo store, the API in the middle,
> and outside the box: OpenAI, Telegram, and the marketplaces.
> *Up in the corner is our review's passport. It picks up a stamp at every stop.*

**0:20** · *02 Sources — reviews stream in, our card walks through the green gate*

> Reviews flow in from WooCommerce, from Lazada, from a simple CSV. And the very first thing
> that happens to our review? The buyer's name is dropped and their phone number is blanked out,
> before anything is even saved. Then it gets a fingerprint, so it can never be counted twice.

**0:35** · *03 Triage — the card falls through the sieve*

> Now, remember those four stars? Triage reads the words, not the rating. And the words say:
> *my laptop doesn't fit.* That's a real complaint, hiding behind a good score.

**0:42** · *04 API key*

> With an OpenAI key plugged in, the AI route opens up.

**0:48** · *05 Credit — coins move to the tray*

> But we don't just call the model and hope. We set aside the worst-case cost first,
> and if it doesn't fit the budget, the call simply doesn't happen.

**0:57** · *06 Privacy — the world pauses*

> And right here, before anything leaves our server, we stop and check. On the left is everything
> OpenAI will see: an ID, a rating, and the cleaned-up text. On the right is everything it never sees:
> the buyer's name, their contact details, the seller's account.
> And we send it with *store set to false*, so it isn't kept on their side.

**1:05** · *07 OpenAI — the envelope flies up, answers come back*

> Only then does it go out. The model comes back with suggestions, we pay only for what was
> actually used, and every one of the hundred and fifty reviews gets sorted.
> *That orange square? That's ours, backing up a sizing problem.*

**1:21** · *08 Fallback — switches flip to the rule engine*

> And if the key is missing, rejected, or the budget runs dry, nothing breaks. Deciqo quietly
> switches to its own rules and gives you the same kind of answer.

**1:34** · *09 Code veto — quotes checked, a paraphrase gets dropped*

> Here's the part we care about most. The model can suggest, but it doesn't get the final word.
> Every quote has to match the review exactly. Make something up, and it's thrown out.
> Even inside our one review, the praise is set aside and only the complaint is kept.

**1:48** · *10 Hold — "needs your fact"; "ok" is rejected, 32 × 24 cm is accepted*

> So here's the catch: the listing never says how big the inside is. Most tools would just guess.
> Deciqo holds, and asks the one person who actually knows: the seller.
> "Ok" isn't an answer. "Thirty-two by twenty-four centimetres" is. And now the gate opens.

**2:04** · *11 Decide — "applied · monitoring"*

> The seller makes the call, and the fix goes live.

**2:08** · *12 Watch — our card is placed on the timeline; a new review reopens the issue*

> But the story doesn't end there. Our review was written before the fix, so it's no longer held
> against the product. Then a new one comes in: *still doesn't fit.* That's after the fix, so the
> issue reopens, and the seller gets a heads-up on Telegram, with no customer text in it.

**2:24** · *pull back, Qo waves, Deciqo lock-up*

> One review, followed all the way through.
> The model proposes. Code decides. And the seller always has the final say.
> That's Deciqo.
>
> *(let the logo sit, and hand over at 2:38)*

---

About 360 words. If you're running behind, drop the passport line at 0:08 and the orange-square line at 1:05 first.

## Keep in your back pocket for Q&A

- **The dollar figures on screen** ($5.000 → $4.971 → $4.993, $0.029 reserved / $0.007 settled) are illustrative. They're computed
  with the engine's own formula (input ≈ characters ÷ 2 at $0.25/M, output = max tokens at $2.00/M). The measured cost is in
  `docs/worklog/engine.md`.
- **From the code:** up to 45 candidates, 150 reviews labelled in 3 batches of 50, at most 8 findings, gpt-5-mini through the
  Responses API with a strict JSON schema.
- **Privacy:** `store=False` is set in `apps/api/app/deciqo/engine/llm.py`. The test `test_panggilan_openai_tidak_disimpan_dan_tanpa_pii`
  checks it, and checks that a phone number never reaches the payload. Buyer names aren't stored at all.
- **Honest limit, if asked:** redaction is pattern-based, so a name written freely mid-sentence can slip through.
- **Made up for the video:** the reviewer "Rizky A.", review ID `r_8f2c` and hash `#a3f9`.
