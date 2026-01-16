import streamlit as st
from openai import OpenAI

# 1. Seiten-Konfiguration
# Setzt Titel und Icon im Browser-Tab
st.set_page_config(page_title="Legal Tech Tool", page_icon="§")

# 2. UI: Titel und Beschreibung
st.title("§ Übersetzer für Anwälte §")
st.write("Verwandle Stichpunkte und Alltagssprache in professionelle Formulierungen für anwaltliche Schriftsätze.")

# 3. Setup: API Key sicher laden
# Wir prüfen, ob der Key in den Secrets hinterlegt ist.
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    # Falls der Key fehlt, stoppen wir die App sauber mit einer Warnung
    st.warning("⚠️ Der API-Key fehlt noch. Bitte trage ihn in den Streamlit-Settings unter 'Secrets' ein.")
    st.stop()

# 4. UI: Auswahl-Box für den Kontext
art_des_schriftsatzes = st.selectbox(
    "Für welche Art von Dokument ist der Text?",
    ("Klageschrift", "Klageerwiderung", "Außergerichtliches Schreiben")
)

# 5. UI: Eingabefeld für den User
text_input = st.text_area(
    "Deine Stichpunkte / Rohtext:", 
    height=150, 
    placeholder="Z.B.: Der Gegner lügt, er hat die Ware nie geschickt. Ich bin stinksauer."
)

# 6. Logik: Der Button
if st.button("Formulierungen generieren"):
    # Check: Hat der User überhaupt was eingegeben?
    if not text_input:
        st.info("Bitte gib erst einen Text ein.")
    else:
        # Lade-Animation starten
        with st.spinner("Analysiere Sachverhalt und generiere Varianten..."):
            try:
                # --- PROMPT DEFINITION ---
                
                # Grundlegende Persona und Regeln
                grund_befehl = """
                Du bist ein erfahrener deutscher, sehr gründlicher und gewissenhafter Rechtsanwalt. 
                Formuliere basierend auf der Eingabe einen präzisen Textbaustein für einen Schriftsatz.
                
                WICHTIG - Befolge diese Regeln strikt:
                1. Schlage immer ZWEI unterschiedliche Varianten vor.
                2. PLATZHALTER: Wenn konkrete Daten (Datum, Beträge, Namen) fehlen, nutze eckige Klammern (z.B. `[Datum]`). Erfinde keine Daten!
                3. EMOTIONS-FILTER: Ignoriere emotionale Ausbrüche ("Lügner") und übersetze sie in objektive Fakten ("Vortrag ist unzutreffend").
                4. BEWEISE: Füge am Ende, wo sinnvoll, den Platzhalter für Beweise an (z.B. "Beweis: Zeugnis `[...]`").
                5. KONTEXT: Verzichte auf Anrede/Grußformel.
                """
                
                # Spezifische Anweisungen je nach Auswahl
                if art_des_schriftsatzes == "Klageschrift":
                    stil_anweisung = """
                    Stil: Offensiv, anspruchsbegründend. Stelle den Sachverhalt als feste Tatsachen dar ('Der Beklagte hat...'). 
                    Biete aktiv Beweise an, wenn angebracht.
                    Ziel: Den Richter überzeugen, dass der Anspruch besteht. Arbeite heraus, warum wir im Recht sind.
                    """
                
                elif art_des_schriftsatzes == "Klageerwiderung":
                    stil_anweisung = """
                    Stil: Defensiv, bestreitend. Nutze Formulierungen wie 'Es wird bestritten, dass...' oder 'Der Vortrag der Gegenseite ist unzutreffend'. 
                    Bestreite (ggf. mit Nichtwissen), aber nur, wenn es auch angebracht ist.
                    Ziel: Die Argumente der Gegenseite entkräften und die Beweislast dem Gegner zuschieben.
                    """
                
                else: # Außergerichtlich
                    stil_anweisung = """
                    Stil: Bestimmt und fordernd. Setze klare Fristen und Konsequenzen. 
                    Vermeide Weichmacher und Konjunktive.
                    Ziel: Außergerichtliche Einigung erzwingen und Druck aufbauen.
                    """

                # Zusammensetzen des finalen Prompts für die KI
                kompletter_prompt = f"""
                {grund_befehl}
                
                {stil_anweisung}
                
                Eingabe (Stichpunkte): "{text_input}"
                
                Formatierung der Antwort:
                ### Option 1 (Prägnant & Direkt)
                [Text]
                
                ### Option 2 (Ausführlich & Juristisch fundiert)
                [Text]
                """
                
                # API-Abfrage an OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": kompletter_prompt}],
                    temperature=0.7 # Kreativität leicht bremsen für seriösere Ergebnisse
                )
                
                # Ergebnis extrahieren
                juristen_text = response.choices[0].message.content
                
                # Ergebnis anzeigen
                st.success(f"Vorschläge für: {art_des_schriftsatzes}")
                st.markdown(juristen_text)
                
            except Exception as e:
                # Fehlerbehandlung (z.B. wenn API Guthaben leer ist)
                st.error(f"Ein technischer Fehler ist aufgetreten: {e}")
