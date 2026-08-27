const API_URL = "http://127.0.0.1:8000";

const uploadForm = document.getElementById("upload-form");
const dateiFeld = document.getElementById("datei-feld");
const dateiLabel = document.getElementById("datei-label");
const dateiText = document.getElementById("datei-text");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const dokumenteListe = document.getElementById("dokumente-liste");
const aktualisierenBtn = document.getElementById("aktualisieren-btn");

dateiFeld.addEventListener("change", () => {
  if (dateiFeld.files.length > 0) {
    dateiText.textContent = dateiFeld.files[0].name;
    dateiLabel.classList.add("hat-datei");
    uploadBtn.disabled = false;
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const datei = dateiFeld.files[0];
  if (!datei) return;

  uploadBtn.disabled = true;
  statusAnzeigen("laden", "Dokument wird hochgeladen und indexiert...");

  const formData = new FormData();
  formData.append("file", datei);

  try {
    const antwort = await fetch(`${API_URL}/ingest`, { method: "POST", body: formData });
    if (!antwort.ok) throw new Error(`Serverfehler: ${antwort.status}`);
    statusAnzeigen("erfolg", `„${datei.name}" wurde erfolgreich indexiert.`);
    dateiFeld.value = "";
    dateiText.textContent = "Datei auswählen oder hierher ziehen";
    dateiLabel.classList.remove("hat-datei");
    dokumenteLaden();
  } catch (fehler) {
    statusAnzeigen("fehler", "Fehler beim Upload: " + fehler.message);
  } finally {
    uploadBtn.disabled = false;
  }
});

function statusAnzeigen(typ, text) {
  uploadStatus.className = "status " + typ;
  uploadStatus.textContent = text;
}

async function dokumenteLaden() {
  dokumenteListe.innerHTML = '<div class="platzhalter">Wird geladen...</div>';
  try {
    const antwort = await fetch(`${API_URL}/documents`);
    if (!antwort.ok) throw new Error(`Serverfehler: ${antwort.status}`);
    const dokumente = await antwort.json();

    if (!dokumente || dokumente.length === 0) {
      dokumenteListe.innerHTML = '<div class="platzhalter">Noch keine Dokumente indexiert.</div>';
      return;
    }

    dokumenteListe.innerHTML = "";
    dokumente.forEach(dok => dokumentAnzeigen(dok));
  } catch (fehler) {
    dokumenteListe.innerHTML = `<div class="platzhalter">Fehler beim Laden: ${fehler.message}</div>`;
  }
}

function dokumentAnzeigen(dok) {
  const div = document.createElement("div");
  div.className = "dokument";

  const info = document.createElement("div");
  info.className = "dokument-info";

  const titel = document.createElement("span");
  titel.className = "dokument-titel";
  titel.textContent = dok.title || "Unbenanntes Dokument";
  info.appendChild(titel);

  const meta = document.createElement("span");
  meta.className = "dokument-meta";
  const typ = (dok.type || "?").toUpperCase();
  const chunks = dok.chunk_count != null ? ` · ${dok.chunk_count} Chunks` : "";
  meta.textContent = `${typ}${chunks}`;
  info.appendChild(meta);

  div.appendChild(info);

  const loeschenBtn = document.createElement("button");
  loeschenBtn.className = "loeschen-btn";
  loeschenBtn.textContent = "Löschen";
  loeschenBtn.addEventListener("click", () => dokumentLoeschen(dok.id, dok.title));
  div.appendChild(loeschenBtn);

  dokumenteListe.appendChild(div);
}

async function dokumentLoeschen(id, titel) {
  if (!confirm(`„${titel}" wirklich löschen?`)) return;
  try {
    const antwort = await fetch(`${API_URL}/document/${encodeURIComponent(id)}`, { method: "DELETE" });
    if (!antwort.ok) throw new Error(`Serverfehler: ${antwort.status}`);
    dokumenteLaden();
  } catch (fehler) {
    alert("Fehler beim Löschen: " + fehler.message);
  }
}

aktualisierenBtn.addEventListener("click", dokumenteLaden);
dokumenteLaden();