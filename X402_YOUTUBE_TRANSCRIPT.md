# Bankr x402 — YouTube Transcript

This branch adds four paid discovery aliases backed by one transcript handler:

- `youtube-transcript`
- `youtube-captions`
- `youtube-subtitles`
- `video-transcript`

All four are priced at **$0.005 USDC/request** on Base using the exact payment scheme.

## What the endpoint returns

- resolved YouTube video ID
- selected caption language and language name
- auto-generated vs manual caption flag
- full LLM/RAG-ready transcript text
- timestamped transcript segments
- list of available caption languages

The handler accepts either a YouTube URL or 11-character video ID via `?video=` and an optional preferred caption language via `?language=`.

## Deploy

From the repository root in an authenticated Bankr CLI environment:

```bash
bankr x402 deploy
```

After deployment, verify each service individually:

```bash
bankr x402 list
bankr x402 revenue youtube-transcript
bankr x402 revenue youtube-captions
bankr x402 revenue youtube-subtitles
bankr x402 revenue video-transcript
```

Revenue should be measured per endpoint using `bankr x402 revenue <service>`, not by attributing all deposits to a shared settlement wallet.

## Discovery metadata

Descriptions and tags deliberately cover these high-intent concepts: YouTube transcript, captions, subtitles, video transcript, timestamps, multilingual captions, LLM, RAG, embeddings, and speech-to-text.
