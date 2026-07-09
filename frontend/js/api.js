const tg = window.Telegram?.WebApp;
const initData = tg?.initData || "";

async function request(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData,
      ...(opts.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${body}`);
  }
  return res.json();
}

export const api = {
  categories: () => request("/api/categories"),
  home: () => request("/api/home"),
  products: (category) => request(`/api/products${category ? `?category=${category}` : ""}`),
  product: (id) => request(`/api/products/${id}`),
  compare: (id) => request(`/api/products/${id}/compare`),
  search: (q) => request(`/api/search?q=${encodeURIComponent(q)}`),
  favorites: () => request("/api/favorites"),
  toggleFavorite: (id) => request(`/api/favorites/toggle/${id}`, { method: "POST" }),
  cart: () => request("/api/cart"),
  addToCart: (product_id, qty = 1) =>
    request("/api/cart/add", { method: "POST", body: JSON.stringify({ product_id, qty }) }),
  removeFromCart: (cartItemId) => request(`/api/cart/remove/${cartItemId}`, { method: "POST" }),
  checkout: (payload) => request("/api/orders", { method: "POST", body: JSON.stringify(payload) }),
};

export { tg };
