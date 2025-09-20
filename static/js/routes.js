function refreshData() {
    const btn = document.getElementById("refresh-btn");
    const originalText = btn.innerHTML;

    // 処理中の表示
    btn.innerHTML = "保存中…";
    btn.disabled = true;

    fetch("/refresh", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                alert(`保存完了: ${data.files.length} 件のファイルを保存しました`);
            } else {
                alert(`更新エラー: ${data.message}`);
            }
        })
        .catch(error => {
            console.error("更新エラー:", error);
            alert("更新に失敗しました");
        })
        .finally(() => {
            // 元のボタン表示に戻す
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
}