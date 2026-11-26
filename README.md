# 🐸 Flappy Frog
Mini pet virtual, scris doar în Python (NiceGUI).

## Cerințe
- Python 3.10+

## Pornire rapidă
```bash
pip install -r requirements.txt
python app.py          # apoi deschide http://localhost:8081

- `/`       jocul (hrănește, spală, schimbă mood-ul, bare de stare)
- `/widget` doar broscuța: ochii urmăresc cursorul, o poți mângâia, click = intri în joc
- `/chat`   chat cu broscuța; răspunde diferit după mood

AI real: `export ANTHROPIC_API_KEY=...` (Windows: `set ANTHROPIC_API_KEY=...`). Fără cheie, folosește replici locale.
Modelul se poate schimba cu variabila `FROG_MODEL`.
