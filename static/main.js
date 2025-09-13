function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const button = document.getElementById("menu-toggle");

    if (sidebar.style.width === "250px") {
        closeSidebar();
    } else {
        sidebar.style.width = "250px";
        overlay.style.display = "block";   // オーバーレイ表示
        button.innerHTML = "&times;";      // ×

        // サイドバー表示中はスクロール禁止
        document.body.style.overflow = "hidden";
    }
}

function closeSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const button = document.getElementById("menu-toggle");

    sidebar.style.width = "0";
    overlay.style.display = "none";       // オーバーレイ非表示
    button.innerHTML = "&#9776;";         // ≡

    // スクロール復活
    document.body.style.overflow = "";
}
