export function formatPrice(n) {
  return n.toLocaleString("ru-RU").replace(/,/g, " ") + " so'm";
}

export function tierBadge(tier) {
  const map = {
    essential: "🥉 Essential",
    recommended: "⭐ Recommended",
    premium: "👑 Premium",
  };
  return map[tier] || tier;
}

export function scoreRing(score) {
  const pct = Math.round((score / 10) * 100);
  return `
    <span class="kivo-score">
      <span class="ring" style="--pct:${pct}"><span>${score}</span></span>
      KIVO ${score}
    </span>`;
}

export function productCardHTML(p) {
  const img = p.image_urls?.[0] || "";
  return `
    <div class="product-card" data-product-id="${p.id}">
      <div class="img-wrap">${img ? `<img src="${img}" alt="${p.name}" loading="lazy" />` : ""}</div>
      <div class="body">
        <span class="badge ${p.tier}">${tierBadge(p.tier)}</span>
        <div class="name">${p.name}</div>
        <div class="price-row">
          <span class="price">${formatPrice(p.price)}</span>
          ${scoreRing(p.kivo_score)}
        </div>
      </div>
    </div>`;
}

export function attachProductCardNav(container, navigate) {
  container.querySelectorAll(".product-card").forEach((el) => {
    el.addEventListener("click", () => navigate(`product/${el.dataset.productId}`));
  });
}

export function backHeaderHTML(title = "") {
  return `
    <div class="header-nav">
      <div class="back-btn" id="back-btn">←</div>
      ${title ? `<div style="font-weight:700;font-size:15px;">${title}</div>` : ""}
    </div>`;
}

export function attachBack(container, navigate, fallback = "home") {
  const btn = container.querySelector("#back-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      if (window.history.length > 1) window.history.back();
      else navigate(fallback);
    });
  }
}
