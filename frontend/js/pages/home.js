import { api, tg } from "../api.js";
import { navigate } from "../main.js";
import { productCardHTML, attachProductCardNav, formatPrice } from "../components.js";

const CAT_ICON = { workspace: "💻", keyboards: "⌨️", mouse: "🖱", usb_hub: "🔌", lighting: "💡", audio: "🎧", organizers: "📦" };

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export async function renderHome(app) {
  const firstName = tg?.initDataUnsafe?.user?.first_name || "";
  const [categories, home] = await Promise.all([api.categories(), api.home()]);

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      <div class="topbar">
        <div class="greet">${greeting()} ${firstName ? "👋" : "👋"}</div>
        <div class="greet-sub">What are you looking for today?</div>
      </div>
      <div class="search-bar" id="search-entry">🔍 <span>Search</span></div>

      <div class="section-title">Categories</div>
      <div class="cat-grid" id="cat-grid">
        ${categories.map((c) => `
          <div class="cat-card" data-cat="${c.key}">
            <div class="icon">${c.icon}</div>
            <div class="label">${c.label}</div>
          </div>`).join("")}
      </div>

      <div class="section-title">Featured</div>
      <div id="featured-list">
        ${home.featured.map(productCardHTML).join("") || `<div class="empty-state">Hozircha yo'q</div>`}
      </div>

      ${home.choice ? `
      <div class="section-title">KIVO Choice ⭐</div>
      <div class="choice-card" id="choice-card">
        <div class="eyebrow">This week's pick</div>
        <h3>${home.choice.name}</h3>
        <div class="price">${formatPrice(home.choice.price)}</div>
        ${home.choice.image_urls?.[0] ? `<img src="${home.choice.image_urls[0]}" />` : ""}
      </div>` : ""}
    </div>`;

  app.querySelectorAll(".cat-card").forEach((el) => {
    el.addEventListener("click", () => navigate(`category/${el.dataset.cat}`));
  });
  attachProductCardNav(app.querySelector("#featured-list"), navigate);
  const choiceCard = document.getElementById("choice-card");
  if (choiceCard) choiceCard.addEventListener("click", () => navigate(`product/${home.choice.id}`));
  document.getElementById("search-entry").addEventListener("click", () => navigate("search"));
}
