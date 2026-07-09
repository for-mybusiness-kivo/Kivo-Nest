import { tg } from "./api.js";
import { renderWelcome } from "./pages/welcome.js";
import { renderHome } from "./pages/home.js";
import { renderCategory } from "./pages/category.js";
import { renderProduct } from "./pages/product.js";
import { renderCart } from "./pages/cart.js";
import { renderCheckout } from "./pages/checkout.js";
import { renderSuccess } from "./pages/success.js";
import { renderFavorites } from "./pages/favorites.js";
import { renderProfile } from "./pages/profile.js";
import { renderSearch } from "./pages/search.js";

if (tg) {
  tg.ready();
  tg.expand();
  tg.setHeaderColor("#FFFFFF");
  tg.setBackgroundColor("#FFFFFF");
}

const app = document.getElementById("app");
const bottomNav = document.getElementById("bottom-nav");

const NAV_ITEMS = [
  { route: "home", icon: "🏠", label: "Home" },
  { route: "search", icon: "🔍", label: "Search" },
  { route: "cart", icon: "🛒", label: "Cart" },
  { route: "favorites", icon: "❤️", label: "Favorites" },
  { route: "profile", icon: "👤", label: "Profile" },
];

const NAV_VISIBLE_ROUTES = new Set(["home", "search", "cart", "favorites", "profile"]);

function renderNav(currentRoute) {
  if (!NAV_VISIBLE_ROUTES.has(currentRoute)) {
    bottomNav.style.display = "none";
    return;
  }
  bottomNav.style.display = "flex";
  bottomNav.innerHTML = NAV_ITEMS.map(
    (item) => `
    <div class="nav-item ${item.route === currentRoute ? "active" : ""}" data-route="${item.route}">
      <div class="icon">${item.icon}</div>
      <div>${item.label}</div>
    </div>`
  ).join("");
  bottomNav.querySelectorAll(".nav-item").forEach((el) => {
    el.addEventListener("click", () => navigate(el.dataset.route));
  });
}

export function navigate(path) {
  window.location.hash = path;
}

const ROUTES = {
  welcome: renderWelcome,
  home: renderHome,
  category: renderCategory,
  product: renderProduct,
  cart: renderCart,
  checkout: renderCheckout,
  success: renderSuccess,
  favorites: renderFavorites,
  profile: renderProfile,
  search: renderSearch,
};

async function router() {
  let hash = window.location.hash.replace("#/", "") || "welcome";
  const [route, ...params] = hash.split("/");
  const renderFn = ROUTES[route] || renderWelcome;

  window.scrollTo(0, 0);
  renderNav(route);

  app.innerHTML = `<div class="page"><div class="skeleton" style="height:200px;"></div></div>`;
  try {
    await renderFn(app, ...params);
  } catch (e) {
    console.error(e);
    app.innerHTML = `<div class="page"><div class="empty-state"><div class="icon">⚠️</div>Xatolik yuz berdi.<br><span style="font-size:12px;color:var(--text-tertiary)">${e.message}</span></div></div>`;
  }
}

window.addEventListener("hashchange", router);
window.addEventListener("DOMContentLoaded", router);
