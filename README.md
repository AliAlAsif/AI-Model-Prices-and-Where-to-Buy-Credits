# AI//PRICES: AI Model Prices and Where to Buy Credits

A single-page, zero-dependency website that compares the API prices of 30 current AI models from 9 providers, shows what each model is good for, and links to where you can buy credits. Neon "digital" interface, light and dark themes, mobile friendly.

> **Unofficial.** This is a community reference, not affiliated with any provider. Prices, promotions and credit terms change often, so confirm on the provider's own page before paying.

**Live site:** https://alialasif.github.io/AI-Model-Prices-and-Where-to-Buy-Credits/ 

## What it shows

- **30 models:** input and output price per million tokens, context size and capability notes. Prices are colored from green (cheap) to magenta (expensive).
- **Cost per request:** enter your own input and output token counts and every model is priced for that request, with a bar for quick comparison. Sort by cost, input, output or provider.
- **Where to buy credits:** a card per provider with links to its console and pricing page, plus what is known about its credit terms.
- **Before you buy** checklist: expiry, auto-reload, taxes, changing prices and aggregators.
- **AUTO / MANUAL tags:** every row says whether its price is synced automatically or edited by hand.

Providers: Anthropic (Claude), OpenAI, Google (Gemini), xAI (Grok), DeepSeek, Mistral, Alibaba (Qwen), Moonshot (Kimi) and the aggregator OpenRouter. It is not every AI model. Meta Llama, Cohere, Amazon Nova, Zhipu, MiniMax and most image, video and audio models are not included.

## Automatic price updates

A GitHub Action (**Sync prices**) runs every day at 05:17 UTC. It downloads OpenRouter's public model catalog (`https://openrouter.ai/api/v1/models`, no API key needed), finds each AUTO model, and writes its current input price, output price and context size back into `index.html`. If anything changed it commits the update, and GitHub Pages republishes the site.

Why OpenRouter: it lists hundreds of models from all the big providers in one JSON file and passes the providers' list prices through without markup.

Safeguards:

- A price change of more than 4× in either direction is **not applied**; it is reported in the run summary for you to check.
- `:batch`, `:free` and other variant IDs are ignored, so a discounted variant cannot overwrite a standard price.
- The run fails (and GitHub emails you) if the catalog looks broken or no model matches.
- A model whose ID is not found simply stays MANUAL. The run summary lists it with the closest IDs so you can fix its mapping.

Limits to know about:

- The catalog can lag a provider's own page, or differ during a promotion. Treat it as a close mirror, not the official source.
- **Notes, context claims in the notes, and credit terms are written by hand** and are never changed by the sync. When a price changes, re-read the note beside it.
- DeepSeek, GPT Realtime and the Gemini image model are MANUAL on purpose, because their prices depend on peak hours or on audio and image units.
- New models are not added automatically. Add them by hand (below).

### One-time setup

1. Upload the files in this repository, including the hidden `.github` folder.
2. Open **Settings → Actions → General**, scroll to **Workflow permissions**, choose **Read and write permissions**, and save. The job needs this to commit.
3. Open the **Actions** tab, choose **Sync prices**, and click **Run workflow**. Open the run and read the summary: it lists changes, blocked changes and any model IDs it could not find.
4. If some models say "not found", edit that model's `or` list in `index.html` using the closest IDs shown, then run the workflow again.

GitHub disables scheduled workflows in a public repository after 60 days without activity. The sync commits at least once a week, which counts as activity. If the schedule ever stops, re-enable it in the **Actions** tab.

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
