# AI//PRICES: AI Model Prices and Where to Buy Credits

A single-page, zero-dependency website that compares the API prices of 30 current AI models from 9 providers, shows what each model is good for, and links to where you can buy credits. Professional blue-and-gold interface set in Times New Roman, with light and dark themes, mobile friendly.

> **Unofficial.** This is a community reference, not affiliated with any provider. Prices, promotions and credit terms change often, so confirm on the provider's own page before paying.

**Live site:** https://alialasif.github.io/AI-Model-Prices-and-Where-to-Buy-Credits/ (after you enable GitHub Pages, see [Deploy](#deploy-to-github-pages))

## What it shows

- **30 models:** input and output price per million tokens, context size and capability notes. Prices are colored blue (cheap) to yellow (expensive).
- **Cost per request:** enter your own input and output token counts and every model is priced for that request, with a bar for quick comparison. Sort by cost, input, output or provider.
- **Five cheapest models chart:** a bar chart of the five cheapest models for your request. It follows the search and provider filters.
- **Search by capability:** the search box matches provider, model name, ID and the capability notes (for example "voice", "coding" or "open weights").
- **Sticky table header:** the column titles stay visible while you scroll the table.
- **Where to buy credits:** a card per provider with links to its console and pricing page, plus what is known about its credit terms.
- **Before you buy** checklist: expiry, auto-reload, taxes, changing prices and aggregators.
- **AUTO / PENDING / MANUAL tags:** AUTO rows were re-priced by the daily sync. PENDING rows are set up for it and wait for the next run (a row that stays PENDING after a run has an OpenRouter ID that was not found). MANUAL rows are edited by hand.

Providers: Anthropic (Claude), OpenAI, Google (Gemini), xAI (Grok), DeepSeek, Mistral, Alibaba (Qwen), Moonshot (Kimi) and the aggregator OpenRouter. It is not every AI model. Meta Llama, Cohere, Amazon Nova, Zhipu, MiniMax and most image, video and audio models are not included.

## Automatic price updates

A GitHub Action (**Sync prices**) runs every day at 05:17 UTC. It downloads OpenRouter's public model catalog (`https://openrouter.ai/api/v1/models`, no API key needed), finds each AUTO model, and writes its current input price, output price and context size back into `index.html`. It commits the update (at minimum the new "last checked" date) and asks GitHub Pages to republish the site.

Why OpenRouter: it lists hundreds of models from all the big providers in one JSON file and passes the providers' list prices through without markup.

Safeguards:

- A price change of more than 4× in either direction is **not applied**; it is reported in the run summary for you to check.
- `:batch`, `:free` and other variant IDs are ignored, so a discounted variant cannot overwrite a standard price.
- The run fails (and GitHub emails you) if the catalog looks broken or no model matches.
- A model whose ID is not found keeps its current price and shows PENDING. The run summary lists it with the closest IDs so you can fix its mapping.
- Dated catalog IDs are handled safely: `mistral-large-3` can match `mistral-large-3-2601`, the newest date wins, and an older dated model is never used in place of a newer one.
- The run retries the download three times before failing, and a catalog with fewer than 50 models is rejected.
- "Last checked" moves on every successful run, and "last price change" moves only when a price changes, not when only a context size changes.

Limits to know about:

- The catalog can lag a provider's own page, or differ during a promotion. Treat it as a close mirror, not the official source.
- **Notes, context claims in the notes, and credit terms are written by hand** and are never changed by the sync. When a price changes, re-read the note beside it.
- DeepSeek, GPT Realtime and the Gemini image model are MANUAL on purpose, because their prices depend on peak hours or on audio and image units.
- New models are not added automatically. Add them by hand (below).

### One-time setup

1. Upload the files in this repository, including the hidden `.github` folder.
2. Open **Settings → Actions → General**, scroll to **Workflow permissions**, choose **Read and write permissions**, and save. The job needs this to commit.
3. Open the **Actions** tab, choose **Sync prices**, and click **Run workflow**. Open the run and read the summary: it lists changes, blocked changes and any model IDs it could not find.
4. If some models stay PENDING or say "not found", edit that model's `or` list in `index.html` using the closest IDs shown, then run the workflow again.

GitHub disables scheduled workflows in a public repository after 60 days without activity. The sync commits every day (it records the date of the last check), which counts as activity. If the schedule ever stops, re-enable it in the **Actions** tab.

## Deploy to GitHub Pages

1. Open **Settings → Pages**.
2. Set **Source** to **Deploy from a branch**, choose `main` and `/ (root)`, and save.
3. After a minute or two the site is live at `https://alialasif.github.io/AI-Model-Prices-and-Where-to-Buy-Credits/`.

## Run locally

```bash
git clone https://github.com/AliAlAsif/AI-Model-Prices-and-Where-to-Buy-Credits.git
cd AI-Model-Prices-and-Where-to-Buy-Credits
python -m http.server 8000     # then visit http://localhost:8000
python scripts/sync_prices.py  # optional: run the price sync yourself
```

## Editing the data

All data lives in one JSON block (`<script type="application/json" id="data">`) near the bottom of `index.html`.

- **Fix a price by hand:** change the model's `i` (input) or `o` (output), in dollars per million tokens. AUTO models will be overwritten by the next sync, so fix those through their `or` list instead.
- **Make a model AUTO:** give it an `or` list of OpenRouter IDs, for example `"or":["openai/gpt-6-luna"]`. The first ID found in the catalog is used.
- **Make a model MANUAL:** delete its `or` list (and `oid`).
- **Add a model:** copy a line in `models` and change `p` (provider key), `m`, `id`, `i`, `o`, `c`, `t` and optionally `or`.
- **Add a provider:** add an entry to `providers` with `k`, `n`, `buy`, `price` and `note`.

## Privacy

The page loads no third-party scripts, fonts or data and never asks for an API key. The daily sync runs on GitHub, not in visitors' browsers.

## Contributing

Pull requests that correct a price, add a verified credit term or add a model are welcome. Please link the official source.

## License

MIT. See [LICENSE](LICENSE).
