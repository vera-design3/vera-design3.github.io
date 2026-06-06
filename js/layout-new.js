/* =========================================================
   淺色版共用版面：導覽列 + 頁尾（極簡風）
   每頁載入這支即可，改連結/信箱只改這裡
   ========================================================= */
const SITE_NEW = {
  email: "vera83610942@gmail.com",
  behance: "https://www.behance.net/ruowei2020da6c",
  linkedin: "https://www.linkedin.com/in/vera-liu-8b979a27a",
  resume: "./Vera Resume.pdf",
  projects: "./index-new.html",
  about: "./about-new.html",
};

const navHTML = `
<header class="nav">
  <div class="nav-inner">
    <a href="${SITE_NEW.projects}" class="brand">Vera Liu <span>· Designer</span></a>
    <nav class="nav-links">
      <a href="${SITE_NEW.projects}">Projects</a>
      <a href="${SITE_NEW.about}">About</a>
      <a href="${SITE_NEW.resume}" target="_blank" rel="noopener">Resume</a>
      <a href="mailto:${SITE_NEW.email}" class="nav-cta">Get in touch</a>
    </nav>
  </div>
</header>`;

const footHTML = `
<footer class="foot">
  <div class="wrap">
    <p class="cta">想合作或聊聊？<br><a href="mailto:${SITE_NEW.email}">${SITE_NEW.email}</a></p>
    <div class="foot-row">
      <span>© <span id="yr"></span> Vera Liu — Taipei, Taiwan</span>
      <span class="links">
        <a href="${SITE_NEW.about}">About</a>
        <a href="${SITE_NEW.behance}" target="_blank" rel="noopener">Behance</a>
        <a href="${SITE_NEW.linkedin}" target="_blank" rel="noopener">LinkedIn</a>
      </span>
    </div>
  </div>
</footer>`;

document.addEventListener("DOMContentLoaded", () => {
  document.body.insertAdjacentHTML("afterbegin", navHTML);
  document.body.insertAdjacentHTML("beforeend", footHTML);
  const yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();
});
