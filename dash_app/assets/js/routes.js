(function waitForButton() {
    const btn = document.getElementById("refresh-btn");

    if (!btn) {
        setTimeout(waitForButton, 300);
        return;
    }

    console.log("refresh-btn found");

    btn.addEventListener("click", async () => {
        const original = btn.innerHTML;
        btn.innerHTML = "保存中…";
        btn.disabled = true;

        try {
            const res = await fetch("/refresh", { method: "POST" });
            const data = await res.json();

            if (data.status === "success") {
                alert(`保存完了: ${data.files.length} 件`);
            } else {
                alert(`エラー: ${data.message}`);
            }
        } catch (e) {
            alert("更新に失敗しました");
        } finally {
            btn.innerHTML = original;
            btn.disabled = false;
        }
    });
})();
