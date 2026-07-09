import { api } from "../api.js";
import { navigate } from "../main.js";
import { productCardHTML, attachProductCardNav, backHeaderHTML, attachBack } from "../components.js";

const TIER_TITLES = {
  essential: "🥉 Essential",
  recommended: "⭐ Recommended",
  premium: "👑 Premium",
};

export async function renderCategory(app, categoryKey) {
  const [categories, grouped] = await Promise.all([api.categories(), api.products(categoryKey)]);
  const cat = categories.find((c) => c.key === categoryKey);

  const hasAny = ["essential", "recommended", "premium"].some((t) => grouped[t]?.length);

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      ${backHeaderHTML(`${cat?.icon || ""} ${cat?.label || categoryKey}`)}
      ${hasAny ? ["essential", "recommended", "premium"].map((tier) => `
        ${grouped[tier]?.length ? `
        <div class="tier-block">
          <div class="tier-label">${TIER_TITLES[tier]}</div>
          <div id="tier-${tier}">${grouped[tier].map(productCardHTML).join("")}</div>
        </div>` : ""}
      `).join("") : `<div class="empty-state"><div class="icon">🧭</div>Bu yo'nalishda hozircha mahsulot yo'q.</div>`}
    </div>`;

  attachBack(app, navigate);
  attachProductCardNav(app, navigate);
}
