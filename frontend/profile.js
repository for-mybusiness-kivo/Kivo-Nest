import { tg } from "../api.js";

export async function renderProfile(app) {
  const user = tg?.initDataUnsafe?.user;

  app.innerHTML = `
    <div class="page" style="padding:0 0 12px;">
      <div class="topbar">
        <div class="greet">${user?.first_name || "Profile"}</div>
        ${user?.username ? `<div class="greet-sub">@${user.username}</div>` : ""}
      </div>
      <div style="margin-top:16px;">
        <div class="profile-row"><span>📦 Buyurtmalar</span><span class="chev">›</span></div>
        <div class="profile-row"><span>❤️ Saqlanganlar</span><span class="chev">›</span></div>
        <div class="profile-row"><span>🌐 Til</span><span class="chev">O'zbekcha</span></div>
        <div class="profile-row"><span>💬 Support</span><span class="chev">›</span></div>
      </div>
    </div>`;
}
