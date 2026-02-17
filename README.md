# 📰 AI News Quiz

A daily news quiz game where you match AI-generated images to headlines.

## Modes

- **Germany** – 4 German news headlines
- **World** – 4 international headlines  
- **Collage** – One artwork hiding 4 stories, pick them from 8 options (Hieronymus Bosch or Van Gogh style)

## Setup

1. Set your `OPENAI_API_KEY` environment variable
2. Run `python3 gen-quiz-images.py` to generate today's images + quiz-data.json
3. Serve the folder as a static website

## Daily Updates

The `gen-quiz-images.py` script fetches today's news and generates DALL-E 3 images. Run it via cron at 7 AM daily.

## Tech

- Vanilla HTML/CSS/JS — no frameworks
- DALL-E 3 for image generation
- Static JSON data file

## Live

→ [shelldon.monoroc.de/games/ai-news-quiz](https://shelldon.monoroc.de/games/ai-news-quiz/)
