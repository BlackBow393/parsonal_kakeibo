// Dashが class を変えた後に副作用だけを処理
const observer = new MutationObserver(() => {
    const sidebar = document.getElementById("sidebar");
    if (!sidebar) return;

    if (sidebar.classList.contains("active")) {
        document.body.style.overflow = "hidden";
    } else {
        document.body.style.overflow = "";
    }
});

window.addEventListener("DOMContentLoaded", () => {
    observer.observe(document.body, { subtree: true, attributes: true });
});
