document.getElementById("selectFolderBtn").addEventListener("click", () => {
        fetch("/select_folder")
        .then(response => response.json())
        .then(data => {
            document.getElementById("folderPath").value = data.folderPath;
        });
    });