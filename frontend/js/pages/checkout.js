import { api, tg } from "../api.js";
import { navigate } from "../main.js";
import { backHeaderHTML, attachBack } from "../components.js";

export async function renderCheckout(app) {
  const tgUser = tg?.initDataUnsafe?.user;
  let location = null;

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      ${backHeaderHTML("Checkout")}

      <div class="field">
        <label>Name</label>
        <input type="text" id="f-name" value="${tgUser ? `${tgUser.first_name || ""} ${tgUser.last_name || ""}`.trim() : ""}" placeholder="Ismingiz" />
      </div>
      <div class="field">
        <label>Phone</label>
        <input type="tel" id="f-phone" placeholder="+998 90 123 45 67" />
      </div>
      <div class="field">
        <label>Address</label>
        <input type="text" id="f-address" placeholder="Ko'cha, uy, xonadon" />
      </div>

      <div class="loc-btn">
        <button class="btn btn-outline" id="loc-btn" type="button">📍 Share Location</button>
      </div>

      <div class="field">
        <label>Comment</label>
        <textarea id="f-comment" rows="3" placeholder="Qo'shimcha izoh (ixtiyoriy)"></textarea>
      </div>

      <div class="sticky-cta">
        <button class="btn btn-primary" id="submit-btn">Place Order</button>
      </div>
    </div>`;

  attachBack(app, navigate);

  document.getElementById("loc-btn").addEventListener("click", () => {
    const btn = document.getElementById("loc-btn");
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          location = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          btn.textContent = "📍 Location shared ✓";
        },
        () => {
          btn.textContent = "📍 Could not get location";
        }
      );
    }
  });

  document.getElementById("submit-btn").addEventListener("click", async () => {
    const name = document.getElementById("f-name").value.trim();
    const phone = document.getElementById("f-phone").value.trim();
    const address = document.getElementById("f-address").value.trim();
    const comment = document.getElementById("f-comment").value.trim();

    if (!name || !phone || !address) {
      tg?.showAlert ? tg.showAlert("Iltimos, Name, Phone va Address maydonlarini to'ldiring.") : alert("Iltimos, barcha maydonlarni to'ldiring.");
      return;
    }

    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Yuborilmoqda...";

    try {
      const res = await api.checkout({
        name, phone, address, comment,
        location_lat: location?.lat, location_lng: location?.lng,
      });
      tg?.HapticFeedback?.notificationOccurred?.("success");
      navigate(`success/${res.order_id}`);
    } catch (e) {
      btn.disabled = false;
      btn.textContent = "Place Order";
      tg?.showAlert ? tg.showAlert("Xatolik yuz berdi, qayta urinib ko'ring.") : alert("Xatolik yuz berdi.");
    }
  });
}
