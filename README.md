# 📰 AI News Quiz

A daily news quiz game where you match AI-generated images to current and historical headlines. Built with vanilla JavaScript and powered by AI image generation.

🎮 **[Play Live](https://shelldon.monoroc.de/games/ai-news-quiz/)**

## 🎯 Game Modes

### Current Events
- **🇩🇪 Germany** – 4 Deutsche news headlines with countdown timer
- **🌍 World** – 4 international headlines with countdown timer
- **🖼️ Collage** – Find 4 hidden stories in one artwork (Bosch or Van Gogh style)

### History
- **🏛️ History** – Match historical events (200 AD – 2010) to AI-generated images
- **🗓️ Year Guess** – Guess the correct year for historical events
- **📅 On This Day** – Events that happened on today's date in history

### Special Modes
- **🎮 Full Day** – Play all categories in one session (12 questions total)
- **📅 Archive** – Replay previous days' quizzes

## ✨ Features

### Gameplay
- ⏱️ **15-second countdown** per question (Current Events & History modes)
- 📊 **Instant feedback** – See correct answers immediately
- 📋 **Quiz Summary** – Detailed review of all your answers with images
- 🎨 **22+ Art Styles** for History mode (Van Gogh, Monet, Picasso, Ukiyo-e, etc.)
- 🎲 **Randomized options** – Different distractors each time

### Progression
- 📈 **Daily Score Tracking** – Track your performance across all modes
- 🏆 **Personal Best** – Keep your highest single-day score
- 🔥 **Streak Counter** – Maintain consecutive days played
- 📊 **Score Widget** – See today's score, best day, and current streak

### Archive System
- 📅 **Browse past quizzes** by date
- 🕐 **Replay any day** – All images and data preserved
- 🗂️ **Automatic archiving** – Previous days moved to archive at midnight

### Mobile & UX
- 📱 **Fully responsive** – Optimized for phone, tablet, desktop
- 🎯 **Auto-hide header** during quiz on mobile
- ♿ **Accessible** – Keyboard navigation, semantic HTML
- 🌙 **Dark theme** – Easy on the eyes

## 🤖 AI Image Generation

### Current Setup (Optimized for Cost)
- **Replicate Flux Schnell** – Germany, World, History events (fast & affordable)
- **OpenAI DALL-E 3** – Collages only (high quality for artistic styles)

### Previous Setup
- **OpenAI DALL-E 3** – All images (higher cost, switched Feb 2026)

### Art Styles Pool (History Mode)
22 different styles randomly applied to historical events:
- **Classic Masters**: Van Gogh, Monet, Rembrandt, Caravaggio, Raphael
- **Modern**: Picasso (Cubism), Dalí (Surrealism), Expressionism (Munch)
- **Decorative**: Art Nouveau (Mucha), Art Deco, Klimt
- **Cultural**: Japanese Ukiyo-e, Medieval Illuminated Manuscripts
- **Contemporary**: Banksy Street Art, Cyberpunk, Hyperrealism
- **Vintage**: 1930s Travel Posters, Soviet Constructivism, Comic Books

## 🛠️ Technical Stack

### Frontend
- **Vanilla JavaScript** – No frameworks, just clean ES6+
- **CSS Grid/Flexbox** – Modern responsive layouts
- **LocalStorage** – Client-side score tracking and archive index

### Backend
- **Python 3** – Image generation script
- **Replicate API** – Flux Schnell model for fast, cheap generation
- **OpenAI API** – DALL-E 3 for collages
- **Static hosting** – Just HTML/CSS/JS + JSON data files

### Data Files
- `quiz-data.json` – Today's quiz (headlines, images, metadata)
- `quiz-data-YYYY-MM-DD.json` – Archived quizzes
- `archive-index.json` – List of available archive dates
- `images/YYYY-MM-DD/` – Archived images

## 🚀 Setup & Deployment

### Prerequisites
```bash
# Required environment variables
export OPENAI_API_KEY="sk-..."
export REPLICATE_API_TOKEN="r8_..."
```

### Generate Today's Quiz
```bash
python3 gen-quiz-images.py
```

This will:
1. Fetch today's top news (Germany + World)
2. Generate 4 Germany + 4 World news images (via Replicate)
3. Pick 4 random historical events from pool (200 AD - 2010)
4. Generate history images in random art styles (via Replicate)
5. Generate 2 collage images per category (Bosch + Van Gogh via DALL-E 3)
6. Archive yesterday's quiz (if exists)
7. Write `quiz-data.json` + images

### Daily Automation (Cron)
```bash
# Run at 7:00 AM daily
0 7 * * * cd /path/to/quiz && OPENAI_API_KEY=$OPENAI_API_KEY REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN python3 gen-quiz-images.py
```

### Serve
```bash
# Any static file server works
python3 -m http.server 8000
# or nginx, Apache, etc.
```

## 📂 Project Structure

```
ai-news-quiz/
├── index.html              # Main quiz app (single-page)
├── gen-quiz-images.py      # Image generation script
├── quiz-data.json          # Today's quiz data
├── quiz-data-2026-02-20.json  # Archived quiz
├── archive-index.json      # List of archive dates
├── images/
│   ├── de1.png            # Today's Germany news
│   ├── wo1.png            # Today's World news
│   ├── hi1.png            # Today's History event
│   ├── collage_germany_bosch.png
│   ├── 2026-02-20/        # Archived images
│   │   ├── de1.png
│   │   └── ...
├── README.md
└── .gitignore
```

## 🎨 How It Works

### Daily Workflow
1. **7:00 AM** – Cron runs `gen-quiz-images.py`
2. Script archives yesterday's data to `images/YYYY-MM-DD/`
3. Fetches today's news via web scraping / news APIs
4. Generates new images via Replicate + OpenAI
5. Writes `quiz-data.json` with today's questions
6. Updates `archive-index.json`

### Quiz Flow
1. User picks a mode (Germany, World, History, Collage, Full Day)
2. App loads `quiz-data.json`
3. Shows AI-generated image + 4 headline options
4. 15-second countdown timer (for timed modes)
5. User picks answer → instant feedback (✅/❌)
6. After all questions → show summary screen
7. Update local score tracking (localStorage)

### Archive System
- When midnight passes, yesterday's quiz is moved to archive
- Archive entry includes:
  - `quiz-data-YYYY-MM-DD.json` (questions + metadata)
  - `images/YYYY-MM-DD/` folder (all images)
  - Entry in `archive-index.json`
- Users can browse and replay any archived day

## 🧠 Historical Events Pool

72+ historical events spanning 200 AD to 2010:
- **Ancient/Medieval** – Fall of Rome, Viking raids, Crusades, Magna Carta
- **Renaissance** – Gutenberg, Columbus, Luther, Copernicus
- **Modern** – French Revolution, Napoleon, Industrial Revolution
- **20th Century** – World Wars, Moon Landing, Berlin Wall, 9/11
- **Art/Science** – Newton, Darwin, Einstein, Penicillin

Each event:
- Has a descriptive prompt for image generation
- Gets a random art style from the 22-style pool
- Year hidden in "Year Guess" mode

## 📊 Score System

### Point Values
- **Germany/World/History**: 1 point per correct answer (max 4)
- **Collage**: 2 points per correct story (max 8)
- **Full Day**: Sum of all categories (max 12)

### Tracking
- **Today's Total**: Sum of your best scores per mode (max 20)
- **Best Day**: Your highest single-day total ever
- **Streak**: Consecutive days with at least 1 mode played

Scores stored in `localStorage` under `quiz_scores` key:
```json
{
  "2026-02-21": {
    "de": 4,
    "world": 3,
    "history": 4,
    "collage": 6
  }
}
```

## 🎯 Roadmap / Future Ideas

- [ ] Leaderboard (Firebase or API)
- [ ] User accounts & cloud sync
- [ ] More categories (Sports, Tech, Entertainment)
- [ ] Difficulty levels (Easy/Medium/Hard)
- [ ] Multiplayer mode
- [ ] Share results to social media
- [ ] RSS feed integration for news
- [ ] AI-generated distractors (fake but plausible headlines)
- [ ] Voice narration mode
- [ ] Accessibility improvements (screen reader, high contrast)

## 🐛 Known Issues

- Archive replay doesn't preserve original art styles (regenerates on load)
- Mobile keyboard can push UI elements off-screen
- No retry limit on failed API calls

## 📝 License

MIT License – Free to use, modify, and distribute.

## 🙏 Credits

- **AI Models**: OpenAI DALL-E 3, Replicate Flux Schnell
- **Design Inspiration**: Wordle, Geoguessr, trivia games
- **Icon**: 📰 News emoji

---

**Made by Shelldon Brooks** 🐚  
[shelldon.monoroc.de](https://shelldon.monoroc.de)
