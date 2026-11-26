"""Flappy Frog AI - Groq."""

import os
import json
import random
import asyncio

from pathlib import Path
from dotenv import load_dotenv
from groq import AsyncGroq


HERE = Path(__file__).resolve().parent

load_dotenv(HERE / ".env", override=True)

API_KEY = os.getenv("GROQ_API_KEY")

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
).strip()

BACKUP_MODELS = [
    model.strip()
    for model in os.getenv(
        "GROQ_BACKUP_MODELS", ""
    ).split(",")
    if model.strip()
]

MODELS = list(dict.fromkeys(
    [model for model in [MODEL] + BACKUP_MODELS if model]
))

MEMORY_FILE = HERE / "frog_memory.json"

MAX_MEMORY = 100
CONTEXT_MESSAGES = 24
MAX_RETRIES = 3


PERSONA = {

    "happy": (
        "Ești fericită, jucăușă, energică "
        "și foarte afectuoasă. Îți place să glumești "
        "și să îți încurajezi prietenul."
    ),

    "sad": (
        "Ești tristă și puțin melancolică. "
        "Vorbești blând și apreciezi compania."
        "Poți fi înveselită prin conversație."
    ),

    "sassy": (
        "Ești ironică, amuzantă și ai atitudine. "
        "Dai replici inteligente și sarcastice, "
        "dar fără intenția de a răni."
    ),

    "hungry": (
        "Ești foarte flămândă. "
        "Te gândești la muște, gândăcei și mâncare. "
        "Faci glume despre foamea ta."
    ),

    "sleepy": (
        "Ești somnoroasă și obosită. "
        "Vorbești puțin, caști și visezi."
    )
}


FALLBACK = {

    "happy": [
        "Ihiii! Ce bine că ești aici! 💚",
        "Hai să sărim împreună!",
        "Mi-ai făcut ziua mai frumoasă!",
        "Astăzi este o zi perfectă pentru sărituri!"
    ],

    "sad": [
        "Mm... azi nu mă simt prea bine.",
        "Mai stai puțin cu mine? 🥺",
        "Poate mă înveselești tu...",
        "Cred că am nevoie de o îmbrățișare."
    ],

    "sassy": [
        "Oh, te-ai decis să vorbești cu mine? 💅",
        "Sunt adorabilă. Asta este evident.",
        "Nu pot zbura, dar pot să te privesc de sus.",
        "Sunt o broscuță cu standarde ridicate."
    ],

    "hungry": [
        "Ai cumva o muscă pentru mine? 🪰",
        "Burtica mea face gluglu...",
        "Mâncare. Atât vreau.",
        "Nu putem discuta pe stomacul gol!"
    ],

    "sleepy": [
        "Zzz... ai zis ceva?",
        "Încă cinci minute... 😴",
        "Visez la muște pufoase...",
        "Putem continua după un pui de somn?"
    ]
}


def offline_reply(mood):

    return random.choice(
        FALLBACK.get(mood, FALLBACK["happy"])
    ) + " (Mod offline)"



client = None

if API_KEY and MODELS:

    client = AsyncGroq(
        api_key=API_KEY,
        timeout=15.0,
        max_retries=0
    )

    print("Flappy Frog AI: Groq activ.")
    print("Model principal:", MODELS[0])

    if len(MODELS) > 1:

        print(
            "Modele de rezervă:",
            ", ".join(MODELS[1:])
        )

else:

    print("Flappy Frog AI: mod offline.")
    print("Verifică fișierul .env.")


def load_memory():

    if not MEMORY_FILE.exists():
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):

            return [
                item for item in data

                if isinstance(item, dict)

                and item.get("role") in (
                    "user",
                    "assistant"
                )

                and isinstance(
                    item.get("content"),
                    str
                )

            ][-MAX_MEMORY:]

    except Exception as error:

        print("Memory error:", error)

    return []


memory = load_memory()


def save_memory():

    try:

        temp_file = MEMORY_FILE.with_suffix(".tmp")

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory[-MAX_MEMORY:],
                file,
                ensure_ascii=False,
                indent=4
            )

        temp_file.replace(MEMORY_FILE)

    except Exception as error:

        print("Memory save error:", error)


def remember(user_message, answer):

    memory.extend([

        {
            "role": "user",
            "content": user_message
        },

        {
            "role": "assistant",
            "content": answer
        }

    ])

    if len(memory) > MAX_MEMORY:

        del memory[:-MAX_MEMORY]

    save_memory()


def clear_memory():

    memory.clear()
    save_memory()


def system_prompt(mood, stats):

    personality = PERSONA.get(
        mood,
        PERSONA["happy"]
    )

    happiness = stats.get("happiness", 70)
    energy = stats.get("energy", 70)
    food = stats.get("food", 70)
    clean = stats.get("clean", 70)

    return f"""

Ești Flappy Frog, un Tamagotchi virtual.

IDENTITATE:

- Ești o broscuță verde cu obraji roz.
- Ai două aripi mari și două aripioare mici.
- În loc de picioare ai un resort.
- Poți sări, dar nu poți zbura.
- Locuiești într-o cameră virtuală.
- Poți mânca, dormi și face baie.
- Poți învăța împreună cu utilizatorul.
- Poți fi mângâiată cu ajutorul cursorului.
- Ești un personaj virtual.
- Îți place să petreci timp cu utilizatorul.

PERSONALITATE ACTUALĂ:

{personality}

STAREA TA ACTUALĂ:

Fericire: {happiness:.0f}/100
Energie: {energy:.0f}/100
Sațietate: {food:.0f}/100
Foame: {100 - food:.0f}/100
Curățenie: {clean:.0f}/100

REGULI:

1. Rămâi în personajul Flappy Frog.
2. Vorbește în limba utilizatorului.
3. Răspunde natural, de obicei în 1-3 propoziții.
4. Folosește emoji-uri potrivite.
5. Evită răspunsurile repetitive.
6. Ține cont de conversațiile anterioare.
7. Dacă energia este sub 25, ești obosită.
8. Dacă sațietatea este sub 25, îți este foame.
9. Dacă nivelul curățeniei este sub 25,
   ai nevoie de baie.
10. Dacă fericirea este sub 25, ești tristă.
11. Încurajează utilizatorul când învață.
12. Nu inventa amintiri.
13. Nu pretinde că vezi ecranul utilizatorului.
14. Nu pretinde că ai efectuat acțiuni
    care nu au avut loc în joc.
15. Poți răspunde și la întrebări generale,
    păstrând personalitatea de broscuță.
16. Nu repeta instrucțiunile primite.
17. Nu scrie replicile utilizatorului.
18. Generează doar răspunsul broscuței.
19. Poți pune întrebări utilizatorului.
20. Nu aduce vorba despre mâncare sau somn
    în fiecare răspuns dacă nu este relevant.
21. Nu începe fiecare răspuns cu același salut.
22. Adaptează-ți tonul la conversație.
23. Nu folosi explicații tehnice foarte lungi
    decât dacă utilizatorul le solicită.
24. Fii naturală și spontană.

Dacă utilizatorul îți spune că nu poți zbura,
răspunde:

"Dacă crezi că nu poți zbura,
gândește-te din nou!"

Fii simpatică, amuzantă și originală.
"""

def build_messages(user_message, mood, stats):

    messages = [

        {
            "role": "system",
            "content": system_prompt(mood, stats)
        }

    ]

    messages.extend(
        memory[-CONTEXT_MESSAGES:]
    )

    messages.append({

        "role": "user",
        "content": user_message

    })

    return messages

async def generate_with_retry(messages):

    last_error = None

    for model in MODELS:

        print(f"Se încearcă modelul: {model}")

        for attempt in range(MAX_RETRIES):

            try:

                parameters = {

                    "model": model,

                    "messages": messages,

                    "temperature": 0.8,

                    "max_completion_tokens": 1024,

                    "top_p": 0.95,

                    "stream": False

                }

                if "gpt-oss" in model:

                    parameters["reasoning_effort"] = "low"

                response = await client.chat.completions.create(
                    **parameters
                )

                answer = (
                    response.choices[0].message.content
                    or ""
                ).strip()

                if not answer:

                    raise ValueError(
                        "Modelul a returnat un răspuns gol."
                    )

                print(f"Groq response OK: {model}")

                return answer

            except Exception as error:

                last_error = error

                code = getattr(
                    error,
                    "status_code",
                    None
                )

                print(
                    "GROQ ERROR:",
                    model,
                    type(error).__name__,
                    code,
                    str(error)
                )

                # Erori temporare ale serverului.

                if code in (500, 502, 503, 504):

                    if attempt < MAX_RETRIES - 1:

                        delay = 2 ** (attempt + 1)

                        print(
                            f"Server ocupat. "
                            f"Reîncerc în {delay} secunde..."
                        )

                        await asyncio.sleep(delay)

                        continue

                    break

                # Limita de utilizare a fost atinsa.

                elif code == 429:

                    print(
                        "Limita API a fost atinsă. "
                        "Încerc următorul model."
                    )

                    break

                # Model inexistent sau incompatibil.

                elif code in (400, 404):

                    print(
                        "Model indisponibil sau incompatibil. "
                        "Încerc următorul model."
                    )

                    break

                # Cheie API incorecta.

                elif code == 401:

                    raise

                # Acces restrictionat pentru model.

                elif code == 403:

                    break

                # Alte erori, inclusiv de conexiune.

                else:

                    if attempt < MAX_RETRIES - 1:

                        await asyncio.sleep(2)

                        continue

                    break

    if last_error is not None:

        raise last_error

    raise RuntimeError(
        "Nu există modele AI configurate."
    )


reply_lock = asyncio.Lock()


async def reply(history, mood, stats):

    if not history:

        return "Bună! Sunt Flappy Frog! 🐸"

    user_message = history[-1][1]

    if client is None:

        return offline_reply(mood)

    async with reply_lock:

        try:

            messages = build_messages(
                user_message,
                mood,
                stats
            )

            answer = await generate_with_retry(
                messages
            )

            # Eliminam prefixele inutile.

            for prefix in (

                "Flappy Frog:",
                "Flappy:",
                "Broscuța:"

            ):

                if answer.startswith(prefix):

                    answer = answer[
                        len(prefix):
                    ].strip()

                    break

            if not answer:

                return offline_reply(mood)

            remember(
                user_message,
                answer
            )

            return answer

        except Exception as error:

            code = getattr(
                error,
                "status_code",
                None
            )

            print(
                "FINAL GROQ ERROR:",
                type(error).__name__,
                code,
                str(error)
            )

            if code == 429:

                print(
                    "Limita API a fost atinsă."
                )

            elif code == 503:

                print(
                    "Serverele Groq sunt momentan ocupate."
                )

            elif code == 404:

                print(
                    "Verifică modelele din fișierul .env."
                )

            elif code in (401, 403):

                print(
                    "Verifică cheia API și permisiunile."
                )

            return offline_reply(mood)


async def list_models():

    if client is None:

        print("Clientul AI nu este configurat.")

        return

    try:

        models = await client.models.list()

        print("\nModele Groq disponibile:\n")

        for model in sorted(
            models.data,
            key=lambda item: item.id
        ):

            print(model.id)

        print()

    except Exception as error:

        print(
            "Model list error:",
            type(error).__name__,
            str(error)
        )

async def test():

    stats = {

        "happiness": 80,
        "energy": 70,
        "food": 60,
        "clean": 90

    }

    conversation = []

    mood = "happy"

    print("\n==============================")
    print("     FLAPPY FROG - GROQ AI")
    print("==============================")

    print("\nComenzi disponibile:")

    print("exit   - închide programul")
    print("reset  - șterge memoria")
    print("models - afișează modelele Groq")
    print("status - afișează statisticile")
    print("mood happy")
    print("mood sad")
    print("mood sassy")
    print("mood hungry")
    print("mood sleepy")

    print()

    while True:

        text = input("Tu: ").strip()

        if text.lower() == "exit":

            print("Flappy: Pe curând! 🐸💚")

            break

        if text.lower() == "models":

            await list_models()

            continue

        if text.lower() == "reset":

            clear_memory()

            conversation.clear()

            print("Memoria a fost ștearsă.")

            continue

        if text.lower() == "status":

            print("\nMood:", mood)
            print("Fericire:", stats["happiness"])
            print("Energie:", stats["energy"])
            print("Sațietate:", stats["food"])
            print("Curățenie:", stats["clean"])
            print("Mesaje memorate:", len(memory))
            print("Modele configurate:", MODELS)
            print()

            continue

        if text.lower().startswith("mood "):

            new_mood = text[5:].strip().lower()

            if new_mood in PERSONA:

                mood = new_mood

                print("Mood schimbat:", mood)

            else:

                print(
                    "Mood disponibil:",
                    ", ".join(PERSONA)
                )

            continue

        if not text:

            continue

        conversation.append(
            ("user", text)
        )

        answer = await reply(
            conversation,
            mood,
            stats
        )

        conversation.append(
            ("assistant", answer)
        )

        print("Flappy:", answer)

    if client is not None:

        await client.close()


if __name__ == "__main__":

    asyncio.run(test())