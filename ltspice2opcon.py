# ltspice2opcon
#
# Copyright (c) 2024 Ohbuchi Takeshi
#
# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#
###
# LTspiceで回路作成し、実行した後にできる".net"ファイルを編集して、
# オペアンプコンテストに提出するサブサーキット".sp"ファイルを作成するするプログラム。
# 注1：LTspiceではinp,inm,vdd,vss,outのコネクタを付けること。
# 注2：負荷抵抗など削除する素子は"R01"や"C01"のように素子名の2文字目を"0"とすること。
###

import glob

fname = glob.glob('*.net')  # ”.net”ファイル名を取得

str_search_V = 'V'  # 電源を探すためのシンボル
str_search_vdd = 'vdd 0'  # vddを探すためのシンボル
str_search_vss = '0 vss'  # vssを探すためのシンボル
str_search_del = ('V', '*', ';', '.')  # 電源、コメントアウト、オプション、出力などを削除する行を探すためのシンボル
str_search_CR = '0'  # 負荷抵抗など削除する素子を探すためのシンボル。C01やR01等二文字目を0にすること。

# データのあるファイルを読み込む #
for num_file, input_file in enumerate(fname):
    V = 0  # 電源電圧(V)を記録（正負両電源である場合は絶対値の和）
    read_file = open(input_file, 'r')  # ”.net”ファイル名を読み取りで開く

    try:  # 文字列を全て読み取り”.net”ファイルがunicodeだと読み取りにエラーがでる
        read_str = read_file.readlines()
    except UnicodeError:  # ”.net”ファイルがunicodeだとエラーがでるので、utf-16leを指定して読み込み
        read_file.close()
        read_file = open(fname[0], 'r', encoding='utf_16le')
        read_str = read_file.readlines()

    read_file.close()

    # 電源電圧を計算
    for number_V, line_V in enumerate(read_str):
        if line_V[0] == str_search_V:
            if str_search_vdd in line_V:
                temp = line_V[line_V.find(str_search_vdd) + 6:-1]
                temp = temp.replace('m', 'e-3')
                V = V + float(temp)
            elif str_search_vss in line_V:
                temp = line_V[line_V.find(str_search_vss) + 6:-1]
                temp = temp.replace('m', 'e-3')
                V = V + float(temp)
            else:
                pass
        else:
            pass

    # ファイル書き込み用リストを作成し電源電圧とサブサーキット宣言で初期化
    write_str = ['.param psvoltage=' + str(V) + 'V \n\n', '.subckt opamp inm inp out vdd vss \n']

    for number, line in enumerate(read_str):
        if line[1] == str_search_CR or line.startswith(str_search_del):
            pass  # 不要な行を削除
        else:
            write_str.append(line)

    write_str.append('.ends \n\n')  # サブサーキットの終了宣言をリストに追加
    write_file = open(input_file.replace('.net', '.sp'), 'w')  # ”.sp”ファイルを書き込みで開く
    write_file.writelines(write_str)  # ”.sp”ファイルにリストを書き込み
    write_file.flush()
    write_file.close()
