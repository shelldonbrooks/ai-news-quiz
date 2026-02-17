#!/usr/bin/env python3
"""Generate News Quiz images + quiz-data.json for today (Germany + World categories)"""

import os, json, base64, urllib.request, datetime

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OUT_DIR = "/var/www/shelldon.monoroc.de/games/ai-news-quiz/images"
JSON_PATH = "/var/www/shelldon.monoroc.de/games/ai-news-quiz/quiz-data.json"
MODEL = "dall-e-3"

CATEGORIES = {
    "germany": [
        {
            "id": "de1",
            "headline": "Deutschland erwägt Social-Media-Verbot für Kinder – Koalition arbeitet an konkreten Plänen",
            "source": "DW",
            "prompt": "A smartphone screen showing social media apps, cracked and surrounded by warning signs and a protective shield, a child's hand reaching toward it, dramatic German flag colors in background, editorial illustration style"
        },
        {
            "id": "de2",
            "headline": "Deutsche Wirtschaft stagniert: Nur 1% Wachstum für 2026 erwartet – DIHK fordert Reformen",
            "source": "Reuters",
            "prompt": "A flat growth chart over a grey industrial German city skyline, factory smokestacks barely steaming, businesspeople looking worried at a stagnant graph, muted blue-grey tones, editorial style"
        },
        {
            "id": "de3",
            "headline": "IG Metall und Tesla-Betriebsrat Grünheide im Machtkampf – Geheimdienste warnen vor AfD-Verbotsverfahren",
            "source": "Süddeutsche Zeitung",
            "prompt": "Two opposing forces at a car factory – union workers with flags facing corporate suits, electric sparks in the air, Tesla factory background, intense political atmosphere, photorealistic editorial"
        },
        {
            "id": "de4",
            "headline": "Olympia 2026 Mailand: Deutsche Athleten verpassen Gold – Enttäuschung im Olympia-Team",
            "source": "SZ / DPA",
            "prompt": "A German athlete standing on the Olympic podium in second place, looking down at a silver medal while the gold position is empty, Milan winter mountains in background, cinematic sports photography style"
        }
    ],
    "world": [
        {
            "id": "wo1",
            "headline": "US-Iran nuclear talks resume in Geneva – Trump signals indirect role, says he hopes Iran will 'be reasonable'",
            "source": "Reuters / Indian Express",
            "prompt": "Diplomats across a long negotiating table in a grand Geneva hall, American and Iranian flags on opposite sides, a dove flying overhead, tense but hopeful atmosphere, photorealistic editorial"
        },
        {
            "id": "wo2",
            "headline": "Civil Rights icon Rev. Jesse Jackson dies at age 84 – nation mourns a tireless voice for justice",
            "source": "Democracy Now",
            "prompt": "A rainbow-colored dove ascending over the US Capitol at dusk, civil rights march silhouettes below, golden light breaking through clouds, powerful memorial illustration, warm emotional tones"
        },
        {
            "id": "wo3",
            "headline": "Ukraine and Russia meet in Geneva for US-brokered peace talks – first direct negotiations in years",
            "source": "Democracy Now",
            "prompt": "Two delegations facing each other at a negotiating table in a neutral Swiss conference room, Ukrainian and Russian flags, olive branch on the table, neutral grey tones with a small ray of hope through a window"
        },
        {
            "id": "wo4",
            "headline": "Tarique Rahman sworn in as new Prime Minister of Bangladesh after historic political transition",
            "source": "The Hindu",
            "prompt": "A dignified leader in traditional South Asian dress taking an oath with hand raised, surrounded by officials, Bangladeshi flag and crowd behind, dawn light, photorealistic ceremonial atmosphere"
        }
    ]
}

def generate_image(prompt, filename):
    url = "https://api.openai.com/v1/images/generations"
    data = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "b64_json"
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    img_b64 = result["data"][0]["b64_json"]
    img_bytes = base64.b64decode(img_b64)
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(img_bytes)
    print(f"  ✅ Saved {filename} ({len(img_bytes)//1024}KB)")
    return filename

os.makedirs(OUT_DIR, exist_ok=True)
today = datetime.date.today().isoformat()

quiz_categories = {}
for cat_key, items in CATEGORIES.items():
    quiz_items = []
    for item in items:
        filename = f"{item['id']}.png"
        print(f"\n🖼  [{cat_key.upper()}] {item['headline'][:55]}...")
        try:
            generate_image(item["prompt"], filename)
            quiz_items.append({
                "id": item["id"],
                "headline": item["headline"],
                "source": item["source"],
                "image": f"images/{filename}"
            })
        except Exception as e:
            print(f"  ❌ Error: {e}")
    quiz_categories[cat_key] = quiz_items

quiz_data = {"date": today, "categories": quiz_categories}
with open(JSON_PATH, "w") as f:
    json.dump(quiz_data, f, indent=2, ensure_ascii=False)
print(f"\n✅ quiz-data.json written ({len(quiz_categories)} categories)")
