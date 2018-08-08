#! /usr/bin/env python3
import os
type_folder = ['乗り物', '食べ物', '人物', '生物', '道具']
folder_dict = {}

plyfile_dict = {}


def plyfile_search(folder_path):
    # plyファイルの拡張子を取り除きファイル名だけを返す
    ply_file = []
    for file in os.listdir(folder_path):
        if file.endswith(".ply"):
            ply_file.append(''.join(os.path.splitext(file)[0]))
    return ply_file


def update_plyfile_dict(path, filelist):
    # 1.フォルダに入っているファイル名の辞書
    # {tool', ['filename1', 'filename2', ...]}
    # 2.ファイル名でファイルパスを取り出せるような辞書作成
    # {'f16','/ply3d/ply/vehicle/f16.ply'}
    filelist.sort()  # 昇順に並び替える(a,b,c,..)
    for i in range(len(filelist)):
        key = filelist[i]
        value = path + key + '.ply'
        plyfile_dict.update({key: value})


def get_plyfile_list():
    # 種類別に作ったフォルダをそれぞれ検索し、
    # app.pyが置かれた階層をルートとする絶対パスを作成し、
    # 辞書化する関数に渡す
    global type_folder
    global folder_dict
    plyfolder_path = 'ply'
    for folder_name in type_folder:
        search_folder_path = plyfolder_path + '/' + folder_name + '/'
        plyfile_list = plyfile_search(search_folder_path)
        update_plyfile_dict(search_folder_path, list(plyfile_list))
        folder_dict.update({folder_name: list(plyfile_list)})
    # 辞書の中身確認
    print(plyfile_dict.items())
    # print(folder_dict.items())
    print(sorted(folder_dict.keys())[0])  # python3でも動く辞書の先頭取得


if __name__ == '__main__':
    get_plyfile_list()
