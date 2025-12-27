(function waitForSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    const button  = document.getElementById("menu-toggle");

    if (!sidebar || !overlay || !button) {
        setTimeout(waitForSidebar, 300);
        return;
    }

    button.addEventListener("click", () => {
        if (sidebar.classList.contains("active")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    function openSidebar() {
        sidebar.classList.add("active");
        overlay.style.display = "block";
        button.innerHTML = "×";
        document.body.style.overflow = "hidden";

        // 幅が開いた後に文字表示
        setTimeout(() => {
            sidebar.classList.add("show");
        }, 300);
    }

    function closeSidebar() {
        // ① 文字を先に消す
        sidebar.classList.remove("show");

        // ② 文字が消えてからバーを閉じる
        setTimeout(() => {
            sidebar.classList.remove("active");
            overlay.style.display = "none";
            button.innerHTML = "☰";
            document.body.style.overflow = "";
        }, 500);
    }
})();
