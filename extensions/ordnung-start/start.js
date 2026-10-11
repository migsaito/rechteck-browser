import { destination } from "./destination.mjs";

const status = document.querySelector("#status");
const notes = document.querySelector("#notes");
document.querySelector("#search").addEventListener("submit", event => {
  event.preventDefault();
  const target = destination(document.querySelector("#destination").value);
  if (target) window.location.assign(target);
  else status.textContent = "Digite uma pesquisa ou um endereço HTTP ou HTTPS válido.";
});

// Disable editing until storage has loaded to avoid overwriting a fast first edit.
notes.disabled = true;
try {
  const stored = await browser.storage.local.get("notes");
  notes.value = typeof stored.notes === "string" ? stored.notes.slice(0, 10000) : "";
  notes.disabled = false;
} catch {
  status.textContent = "Não foi possível carregar suas anotações. Reabra esta aba para tentar novamente.";
}
let timer;
let saving = Promise.resolve();
notes.addEventListener("input", () => {
  clearTimeout(timer);
  status.textContent = "Salvando...";
  timer = setTimeout(() => {
    const text = notes.value;
    saving = saving.then(async () => {
      try {
        await browser.storage.local.set({ notes: text });
        if (notes.value === text) status.textContent = "Salvo neste navegador.";
      } catch {
        status.textContent = "Não foi possível salvar suas anotações.";
      }
    });
  }, 250);
});
