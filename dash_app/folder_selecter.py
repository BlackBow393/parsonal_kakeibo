from tkinter import Tk, filedialog

def choose_folder():
    """
    Tkinterのフォルダ選択ダイアログを前面で開き、フルパスを返す
    """
    root = Tk()
    root.withdraw()  # メインウィンドウ非表示
    root.attributes('-topmost', True)  # ダイアログを最前面に表示
    folder_path = filedialog.askdirectory(title="保存先フォルダを選択")
    root.destroy()
    return folder_path
