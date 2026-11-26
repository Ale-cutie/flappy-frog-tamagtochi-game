"""Răspunsurile broscuței: AI (Claude) dacă există ANTHROPIC_API_KEY, altfel replici locale."""
import asyncio, os, random

PERSONA = {
    "happy": "Ești fericită, jucăușă, plină de energie și foarte afectuoasă. Folosești emoji-uri drăguțe.",
    "sad": "Ești tristă și puțin melancolică, vorbești încet, dar apreciezi când cineva e aici cu tine.",
    "sassy": "Ești sassy: ironică, cu atitudine, dai replici șmechere, dar în fond îți pasă.",
    "hungry": "Ești FOARTE flămândă și te gândești doar la mâncare (muște, gândăcei, orice).",
    "sleepy": "Ești somnoroasă, mormăi, scurtezi cuvintele și cascăzi des.",
}
FALLBACK = {
    "happy": ["Ihiii, ce bine că ești aici! 💚", "Azi zbor... adică sar! Tu ce faci?", "Ești cel mai bun om-prieten! ✨"],
    "sad": ["Mm... nu știu, azi nu mă simt prea bine...", "Mă mai ții puțin de vorbă? 🥺", "*oftează într-un arc de resort*"],
    "sassy": ["Oh, te-ai decis să vorbești cu mine? Wow, onoare.", "Nu pot să zbor, dar pot să te privesc de sus. 💅", "Da, sunt adorabilă. Next question."],
    "hungry": ["Mi-e foame... ai vreo muscă? 🪰", "Burtica mea face gluglu...", "Mâncare. Doar atât spun. MÂNCARE."],
    "sleepy": ["zzz... mm? ai zis ceva?", "*cască* mai târziu...", "Poți să vorbești mai încet? Visez..."],
}


def system_prompt(mood, stats):
    return (f"Ești Flappy Frog, o broscuță cu aripioare care nu poate zbura, dar poate sări. {PERSONA[mood]} "
            f"Starea ta: fericire {stats['happiness']}/100, energie {stats['energy']}/100, "
            f"foame {100 - stats['food']}/100, curățenie {stats['clean']}/100. "
            "Răspunde în română, scurt (1-3 propoziții), rămâi mereu în personaj. "
            "Dacă ți se spune că nu poți zbura, răspunde: dacă crezi că nu poți zbura, gândește-te din nou!")


async def reply(history, mood, stats):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return random.choice(FALLBACK[mood]) + "  (mod offline: setează ANTHROPIC_API_KEY pentru AI)"
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msgs = [{"role": r, "content": t} for r, t in history[-12:]]
        r = await asyncio.to_thread(
            client.messages.create, model=os.getenv("FROG_MODEL", "claude-sonnet-4-6"),
            max_tokens=300, system=system_prompt(mood, stats), messages=msgs)
        return r.content[0].text
    except Exception as e:
        return random.choice(FALLBACK[mood]) + f"  (eroare AI: {type(e).__name__})"
