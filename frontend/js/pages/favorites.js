import { api } from "../api.js";
import { navigate } from "../main.js";
import { productCardHTML, attachProductCardNav } from "../components.js";

export async function renderFavorites(app) {
  const favorites = await api.favorites();

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      <div class="topbar"><div class="greet">Favorites</div></div>
      ${favorites.length
        ? `<div id="fav-list" style="margin-top:12px;">${favorites.map(productCardHTML).join("")}</div>`
        : `<div class="empty-state"><div class="icon">❤️</div>Hali hech narsa saqlamagansiz.</div>`}
    </div>`;

  attachProductCardNav(app, navigate);
}
