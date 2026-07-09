import { api, tg } from "../api.js";
import { navigate } from "../main.js";
import { formatPrice, tierBadge, backHeaderHTML, attachBack } from "../components.js";

function scoreRow(label, val) {
  return `
    <div class="score-row">
      <span class="label">${label}</span>
      <span class="bar"><span style="width:${val * 10}%"></span></span>
      <span class="val">${val}</span>
    </div>`;
}

export async function renderProduct(app, id) {
  const [product, compareList, favorites] = await Promise.all([
    api.product(id),
    api.compare(id),
    api.favorites().catch(() => []),
  ]);
  const isFav = favorites.some((f) => f.id === product.id);

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;position:relative;">
      ${backHeaderHTML()}
      <div class="fav-btn" id="fav-btn" style="position:absolute;top:16px;right:20px;">${isFav ? "❤️" : "🤍"}</div>

      <div class="pdp-gallery">
        ${(product.image_urls?.length ? product.image_urls : [""]).map((src) => `<img src="${src}" />`).join("")}
      </div>

      <div class="pdp-header">
        <span class="badge ${product.tier}">${tierBadge(product.tier)}</span>
        ${product.is_choice ? `<span class="badge recommended" style="margin-left:6px;">⭐ KIVO Choice</span>` : ""}
        <div class="name">${product.name}</div>
        <div class="price">${formatPrice(product.price)}</div>
      </div>

      <div class="block">
        <h4>Why we recommend it</h4>
        <ul class="reason-list why">
          ${product.why_recommend.map((r) => `<li>${r}</li>`).join("")}
        </ul>
      </div>

      ${product.not_for_you?.length ? `
      <div class="block">
        <h4>Not for you if</h4>
        <ul class="reason-list not">
          ${product.not_for_you.map((r) => `<li>${r}</li>`).join("")}
        </ul>
      </div>` : ""}

      <div class="score-panel">
        <div class="top-line"><span class="title">Why KIVO selected this</span></div>
        <div class="considered">${product.models_considered} ta model ichidan tanlandi</div>
        <div class="score-rows">
          ${scoreRow("Narx/Sifat", product.price_quality_score)}
          ${scoreRow("Build", product.build_score)}
          ${scoreRow("Design", product.design_score)}
          ${scoreRow("Durability", product.durability_score)}
        </div>
        <div class="score-total">
          <span>KIVO Score</span>
          <span class="big">${product.kivo_score}<small>/10</small></span>
        </div>
      </div>

      <div class="section-title" style="margin-top:0;">Compare</div>
      <div class="compare-row" id="compare-row">
        ${compareList.map((c) => `
          <div class="compare-col ${c.id === product.id ? "active" : ""}" data-id="${c.id}">
            <span class="badge ${c.tier}">${tierBadge(c.tier)}</span>
            <div class="price">${formatPrice(c.price)}</div>
          </div>`).join("")}
      </div>

      <div class="sticky-cta">
        <button class="btn btn-primary" id="add-cart-btn" ${!product.in_stock ? "disabled" : ""}>
          ${product.in_stock ? "Add to Cart" : "Out of stock"}
        </button>
      </div>
    </div>`;

  attachBack(app, navigate);

  document.getElementById("fav-btn").addEventListener("click", async (e) => {
    const res = await api.toggleFavorite(product.id);
    e.target.textContent = res.favorited ? "❤️" : "🤍";
  });

  document.getElementById("add-cart-btn").addEventListener("click", async () => {
    await api.addToCart(product.id, 1);
    tg?.HapticFeedback?.notificationOccurred?.("success");
    navigate("cart");
  });

  app.querySelectorAll(".compare-col").forEach((el) => {
    el.addEventListener("click", () => {
      if (Number(el.dataset.id) !== product.id) navigate(`product/${el.dataset.id}`);
    });
  });
}
