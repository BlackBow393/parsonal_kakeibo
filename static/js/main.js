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

        // サイドバーが開ききった後（0.3秒後）にメニューをフェードイン
        setTimeout(() => {
            sidebar.classList.add("show");
        }, 300);
        
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

    // クラスを外して再度非表示状態に
    sidebar.classList.remove("show");
    
    // --- STEP 2: aタグが完全に消えてから（0.4秒後）幅を閉じる ---
    setTimeout(() => {
        sidebar.style.width = "250px"; // ← 一旦幅を固定
    }, 0);

    setTimeout(() => {
        sidebar.style.width = "0";
    }, 400);

    // --- STEP 3: サイドバーが閉じきった後にクリーンアップ ---
    setTimeout(() => {
        sidebar.classList.remove("open");
        overlay.style.display = "none";
        button.innerHTML = "&#9776;";
        document.body.style.overflow = "auto";
    }, 700); // 400ms（フェードアウト） + 300ms（スライドアウト）
    
    // スクロール復活
    document.body.style.overflow = "";
}

window.addEventListener("DOMContentLoaded", function() {
    const iframe = document.getElementById("analysis-frame");
    const overlay = document.getElementById("loading-overlay");

    // iframe が完全に読み込まれたらオーバーレイを消す
    iframe.addEventListener("load", function() {
        overlay.style.transition = "opacity 0.5s ease";
        overlay.style.opacity = "0";

        // 完全に透明になった後で display: none に
        setTimeout(() => {
            overlay.style.display = "none";
        }, 500);
    });
});