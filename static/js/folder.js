document.getElementById("folderInput").addEventListener("change", function() {
    const files = this.files;
    if (files.length > 0) {
        // 選択フォルダの相対パスを取得（最初のファイルから）
        const relativePath = files[0].webkitRelativePath;
        const folderOnly = relativePath.substring(0, relativePath.lastIndexOf("/"));

        // Flaskに送信してフルパスに変換
        fetch("/get_fullpath", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ relativePath: folderOnly })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("folderPath").value = data.fullPath;
        });
    }
});
