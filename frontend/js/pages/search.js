import { api } from "../api.js";
import { navigate } from "../main.js";
import { productCardHTML, attachProductCardNav } from "../components.js";

let debounceTimer;

export async function renderSearch(app) {
  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      <div class="topbar" style="padding-bottom:0;">
        <div class="greet">Search</div>
        <div class="greet-sub">Masalan: "need laptop for university"</div>
      </div>
      <div class="search-bar" style="cursor:text;">
        🔍 <input id="search-input" type="text" placeholder="Nima izlayapsiz?" autofocus />
      </div>
      <div id="results" style="margin-top:8px;"></div>
    </div>`;

  const input = document.getElementById("search-input");
  const results = document.getElementById("results");

  input.addEventListener("input", () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();
    if (!q) {
      results.innerHTML = "";
      return;
    }
    results.innerHTML = `<div class="empty-state" style="padding:30px;"><div class="skeleton" style="height:14px;width:60%;margin:0 auto;"></div></div>`;
    debounceTimer = setTimeout(async () => {
      const products = await api.search(q);
      results.innerHTML = products.length
        ? products.map(productCardHTML).join("")
        : `<div class="empty-state"><div class="icon">🔍</div>Hech narsa topilmadi. Boshqacha so'z bilan urinib ko'ring.</div>`;
      attachProductCardNav(results, navigate);
    }, 450);
  });
}
