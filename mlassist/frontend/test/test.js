const API_URL = "http://127.0.0.1:8000";

const form = document.getElementById("test-form");
const dateiFeld = document.getElementById("datei-feld");
const dateiLabel = document.getElementById("datei-label");
const dateiText = document.getElementById("datei-text");
const frageFeld = document.getElementById("frage-feld");
const sendenBtn = document.getElementById("senden-btn");
const antwortBereich = document.getElementById("antwort-bereich");
const antwortText = document.getElementById("antwort-text");

// Datei ausgewählt -> Label aktualisieren
dateiFeld.addEventListener("change", () => {
  if (dateiFeld.files.length > 0) {
    dateiText.textContent = dateiFeld.files[0].name;
    dateiLabel.classList.add("hat-datei");
    pruefeBereit();
  }
});

// Frage getippt -> prüfen ob abschickbar
frageFeld.addEventListener("input", pruefeBereit);

// Button nur freigeben, wenn Datei UND Frage vorhanden sind
function pruefeBereit() {
  sendenBtn.disabled = !(dateiFeld.files.length > 0 && frageFeld.value.trim());
}

// Formular absenden
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const datei = dateiFeld.files[0];
  const frage = frageFeld.value.trim();
  if (!datei || !frage) return;

  sendenBtn.disabled = true;
  antwortBereich.classList.remove("versteckt");
  antwortText.className = "antwort-text laden";
  antwortText.textContent = "Dokument wird analysiert...";

  // Datei + Frage als FormData senden (Datei -> kein JSON)
  const formData = new FormData();
  formData.append("file", datei);
  formData.append("question", frage);
  formData.append("mode", "A");

  try {
    const antwort = await fetch(`${API_URL}/test-query`, {
      method: "POST",
      body: formData
    });
    if (!antwort.ok) throw new Error(`Serverfehler: ${antwort.status}`);
    const daten = await antwort.json();
    antwortText.className = "antwort-text";
    antwortText.textContent = daten.answer;
  } catch (fehler) {
    antwortText.className = "antwort-text";
    antwortText.textContent = "Fehler: " + fehler.message;
  } finally {
    sendenBtn.disabled = false;
  }
});