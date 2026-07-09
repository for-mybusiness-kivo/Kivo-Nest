import { navigate } from "../main.js";

export async function renderWelcome(app) {
  app.innerHTML = `
    <div class="welcome">
      <div class="mark">K</div>
      <h1>KIVO NEST</h1>
      <div class="sub">Curated Workspace &amp; Tech</div>
      <button class="btn btn-primary enter-btn" id="enter-btn">Enter Store</button>
      <div class="proof">
        <div>⭐ 200+ happy customers</div>
        <div>🚚 Fast Delivery</div>
        <div>🔒 Trusted Products</div>
      </div>
    </div>`;

  document.getElementById("enter-btn").addEventListener("click", () => navigate("home"));
}
