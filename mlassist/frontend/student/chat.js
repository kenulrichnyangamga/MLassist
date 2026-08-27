const API_URL = "http://localhost:8000";

const form = document.getElementById("frage-form");
const frageFeld = document.getElementById("frage-feld");
const codeFeld = document.getElementById("code-feld");
const chatFenster = document.getElementById("chat-fenster");
const sendenBtn = document.getElementById("senden-btn");
const modusButtons = document.querySelectorAll(".modus-btn");

// Aktueller Modus, Standard ist A
let aktuellerModus = "A";

// Modus-Umschaltung
modusButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    // aktiven Zustand umsetzen
    modusButtons.forEach(b => b.classList.remove("aktiv"));
    btn.classList.add("aktiv");
    aktuellerModus = btn.dataset.mode;

    // Code-Feld nur in Modus B anzeigen
    if (aktuellerModus === "B") {
      codeFeld.classList.remove("versteckt");
    } else {
      codeFeld.classList.add("versteckt");
      codeFeld.value = "";
    }
  });
});

// Formular absenden
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const frage = frageFeld.value.trim();
  const code = codeFeld.value.trim();
  if (!frage) return;

  // Frage anzeigen
  nachrichtAnzeigen("frage", "Du", frage);

  frageFeld.value = "";
  sendenBtn.disabled = true;

  // Ladeanzeige einfügen
  const laden = ladeanzeigeEinfuegen();

  try {
    const antwort = await fetch(`${API_URL}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: frage,
        code_context: aktuellerModus === "B" ? (code || null) : null,
        mode: aktuellerModus
      })
    });

    if (!antwort.ok) throw new Error(`Serverfehler: ${antwort.status}`);

    const daten = await antwort.json();
    laden.remove();
    nachrichtAnzeigen("antwort", "MLAssist", daten.answer, daten.sources);

  } catch (fehler) {
    laden.remove();
    nachrichtAnzeigen("antwort", "Fehler", "Es ist ein Problem aufgetreten: " + fehler.message);
  } finally {
    sendenBtn.disabled = false;
    if (aktuellerModus === "B") codeFeld.value = "";
  }
});

// Nachricht einfügen
function nachrichtAnzeigen(typ, rolle, text, quellen = null) {
  const platzhalter = chatFenster.querySelector(".platzhalter");
  if (platzhalter) platzhalter.remove();

  const div = document.createElement("div");
  div.className = "nachricht " + typ;

  const rolleEl = document.createElement("div");
  rolleEl.className = "rolle";
  rolleEl.textContent = rolle;
  div.appendChild(rolleEl);

  const blase = document.createElement("div");
  blase.className = "blase";
  blase.textContent = text;
  div.appendChild(blase);

  if (quellen && quellen.length > 0) {
    const quellenEl = document.createElement("div");
    quellenEl.className = "quellen";
    quellenEl.innerHTML = "<strong>Quellen:</strong>";
    const liste = document.createElement("ul");
    quellen.forEach(q => {
      const li = document.createElement("li");
      const seite = q.page ? `, S. ${q.page}` : "";
      li.textContent = `${q.title}${seite} (Score: ${q.score.toFixed(2)})`;
      liste.appendChild(li);
    });
    quellenEl.appendChild(liste);
    div.appendChild(quellenEl);
  }

  chatFenster.appendChild(div);
  chatFenster.scrollTop = chatFenster.scrollHeight;
}

// Ladeanzeige (drei hüpfende Punkte)
function ladeanzeigeEinfuegen() {
  const div = document.createElement("div");
  div.className = "nachricht antwort";
  div.innerHTML = `<div class="rolle">MLAssist</div>
    <div class="laden"><span></span><span></span><span></span></div>`;
  chatFenster.appendChild(div);
  chatFenster.scrollTop = chatFenster.scrollHeight;
  return div;
}