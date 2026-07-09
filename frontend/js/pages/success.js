import { navigate } from "../main.js";

export async function renderSuccess(app, orderId) {
  app.innerHTML = `
    <div class="success-page">
      <div class="emoji">🎉</div>
      <h2>Order Received</h2>
      <p>Buyurtma #${String(orderId).padStart(4, "0")}<br/>Admin will contact you shortly.</p>
      <button class="btn btn-primary" id="home-btn" style="margin-top:28px;max-width:220px;">Back to Home</button>
    </div>`;

  document.getElementById("home-btn").addEventListener("click", () => navigate("home"));
}
