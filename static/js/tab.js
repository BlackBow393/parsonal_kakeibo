// タブ切替用関数
function switchTab(button) {
    const iframe = document.getElementById('analysis-frame');
    iframe.src = button.dataset.src;

    // ボタンのアクティブ状態を切り替え
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');

    // 読み込み中オーバーレイを表示
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'block';

    // iframe読み込み完了でオーバーレイを非表示
    iframe.onload = function() {
        overlay.style.display = 'none';
    };
}

// ページ読み込み時に最初のタブをアクティブにして iframe に src をセット
document.addEventListener('DOMContentLoaded', function() {
    const activeTab = document.querySelector('.tab-btn.active');
    if(activeTab) {
        // iframeに初期srcをセット
        switchTab(activeTab);
    }
});
