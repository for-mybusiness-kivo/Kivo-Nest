import { api } from "../api.js";
import { navigate } from "../main.js";
import { formatPrice, backHeaderHTML, attachBack } from "../components.js";

export async function renderCart(app) {
  const cart = await api.cart();

  if (!cart.items.length) {
    app.innerHTML = `
      <div class="page">
        ${backHeaderHTML("Cart")}
        <div class="empty-state">
          <div class="icon">🛒</div>
          Savatingiz bo'sh.<br/>
          <button class="btn btn-outline" id="browse-btn" style="margin-top:16px;">Do'konga qaytish</button>
        </div>
      </div>`;
    attachBack(app, navigate);
    document.getElementById("browse-btn").addEventListener("click", () => navigate("home"));
    return;
  }

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      ${backHeaderHTML("Cart")}
      <div id="cart-items">
        ${cart.items.map((i) => `
          <div class="cart-item" data-cart-id="${i.cart_item_id}">
            <img src="${i.product.image_urls?.[0] || ""}" />
            <div class="info">
              <div class="name">${i.product.name}</div>
              <div class="price">${formatPrice(i.product.price)} × ${i.qty}</div>
              <div class="remove" data-remove="${i.cart_item_id}">Remove</div>
            </div>
          </div>`).join("")}
      </div>

      <div class="promo-row">
        <input type="text" placeholder="Promo code" id="promo-input" />
      </div>

      <div class="cart-total-row">
        <span>Total</span>
        <span>${formatPrice(cart.total)}</span>
      </div>

      <div class="sticky-cta">
        <button class="btn btn-primary" id="continue-btn">Continue</button>
      </div>
    </div>`;

  attachBack(app, navigate);
  app.querySelectorAll("[data-remove]").forEach((el) => {
    el.addEventListener("click", async (e) => {
      e.stopPropagation();
      await api.removeFromCart(el.dataset.remove);
      renderCart(app);
    });
  });
  document.getElementById("continue-btn").addEventListener("click", () => navigate("checkout"));
}
