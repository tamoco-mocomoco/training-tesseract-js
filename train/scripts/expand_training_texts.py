#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
training_texts.txt を拡張して、より多くのトレーニングテキストを生成
"""

import random
import itertools

# 都道府県
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県",
    "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
    "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県",
    "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

# 市区町村（都道府県庁所在地・政令指定都市・中核市・東京23区）
CITIES = [
    # 北海道・東北
    "札幌市", "函館市", "旭川市", "青森市", "八戸市", "盛岡市", "仙台市", "秋田市",
    "山形市", "福島市", "郡山市", "いわき市",

    # 関東
    "水戸市", "日立市", "宇都宮市", "小山市", "前橋市", "高崎市",
    "さいたま市", "川越市", "川口市", "所沢市", "越谷市", "草加市", "春日部市",
    "千葉市", "船橋市", "松戸市", "市川市", "柏市",

    # 東京都（23区）
    "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
    "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
    "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区",

    # 東京都（市部）
    "八王子市", "立川市", "武蔵野市", "三鷹市", "府中市", "町田市", "調布市", "西東京市",

    # 神奈川県
    "横浜市", "川崎市", "相模原市", "横須賀市", "藤沢市", "平塚市", "小田原市", "厚木市",

    # 中部
    "新潟市", "長岡市", "富山市", "金沢市", "福井市", "甲府市", "長野市", "松本市",
    "岐阜市", "大垣市", "静岡市", "浜松市", "沼津市", "富士市",
    "名古屋市", "豊橋市", "岡崎市", "一宮市", "春日井市", "豊田市",
    "津市", "四日市市",

    # 近畿
    "大津市", "京都市", "宇治市",
    "大阪市", "堺市", "東大阪市", "豊中市", "吹田市", "高槻市", "枚方市", "茨木市", "八尾市",
    "神戸市", "姫路市", "尼崎市", "明石市", "西宮市", "芦屋市", "宝塚市",
    "奈良市", "和歌山市",

    # 中国
    "鳥取市", "米子市", "松江市", "出雲市", "岡山市", "倉敷市",
    "広島市", "呉市", "福山市", "尾道市", "山口市", "下関市",

    # 四国
    "徳島市", "高松市", "松山市", "今治市", "高知市",

    # 九州・沖縄
    "北九州市", "福岡市", "久留米市", "佐賀市", "長崎市", "佐世保市",
    "熊本市", "大分市", "宮崎市", "鹿児島市", "那覇市", "浦添市"
]

# 政令指定都市の区
CITY_WARDS = [
    # 札幌市
    "中央区", "北区", "東区", "白石区", "豊平区", "南区", "西区", "厚別区", "手稲区", "清田区",
    # 仙台市
    "青葉区", "宮城野区", "若林区", "太白区", "泉区",
    # さいたま市
    "西区", "北区", "大宮区", "見沼区", "中央区", "桜区", "浦和区", "南区", "緑区", "岩槻区",
    # 千葉市
    "中央区", "花見川区", "稲毛区", "若葉区", "緑区", "美浜区",
    # 横浜市
    "鶴見区", "神奈川区", "西区", "中区", "南区", "港南区", "保土ケ谷区", "旭区",
    "磯子区", "金沢区", "港北区", "緑区", "青葉区", "都筑区", "戸塚区", "栄区", "泉区", "瀬谷区",
    # 川崎市
    "川崎区", "幸区", "中原区", "高津区", "宮前区", "多摩区", "麻生区",
    # 相模原市
    "緑区", "中央区", "南区",
    # 新潟市
    "北区", "東区", "中央区", "江南区", "秋葉区", "南区", "西区", "西蒲区",
    # 静岡市
    "葵区", "駿河区", "清水区",
    # 浜松市
    "中区", "東区", "西区", "南区", "北区", "浜北区", "天竜区",
    # 名古屋市
    "千種区", "東区", "北区", "西区", "中村区", "中区", "昭和区", "瑞穂区",
    "熱田区", "中川区", "港区", "南区", "守山区", "緑区", "名東区", "天白区",
    # 京都市
    "北区", "上京区", "左京区", "中京区", "東山区", "下京区", "南区",
    "右京区", "伏見区", "山科区", "西京区",
    # 大阪市
    "都島区", "福島区", "此花区", "西区", "港区", "大正区", "天王寺区", "浪速区",
    "西淀川区", "東淀川区", "東成区", "生野区", "旭区", "城東区", "阿倍野区",
    "住吉区", "東住吉区", "西成区", "淀川区", "鶴見区", "住之江区", "平野区", "北区", "中央区",
    # 堺市
    "堺区", "中区", "東区", "西区", "南区", "北区", "美原区",
    # 神戸市
    "東灘区", "灘区", "兵庫区", "長田区", "須磨区", "垂水区", "北区", "中央区", "西区",
    # 岡山市
    "北区", "中区", "東区", "南区",
    # 広島市
    "中区", "東区", "南区", "西区", "安佐南区", "安佐北区", "安芸区", "佐伯区",
    # 北九州市
    "門司区", "若松区", "戸畑区", "小倉北区", "小倉南区", "八幡東区", "八幡西区",
    # 福岡市
    "東区", "博多区", "中央区", "南区", "西区", "城南区", "早良区",
    # 熊本市
    "中央区", "東区", "西区", "南区", "北区",
]

# 町名（住所認識精度向上のため大幅に拡充）
TOWNS = [
    # 方角系
    "中央", "北", "南", "東", "西", "北東", "南西", "北西", "南東",
    # 基本的な町名
    "本町", "新町", "上町", "下町", "中町", "元町", "旧町", "大町", "小町",
    # 自然・植物系
    "緑町", "桜", "松", "竹", "梅", "若葉", "青葉", "緑", "泉", "花園",
    "桜木", "柳", "杉", "檜", "桐", "楠", "欅", "銀杏",
    # 地形系
    "山", "川", "海", "丘", "台", "坂", "谷", "平", "野", "原", "田", "畑",
    "山手", "川端", "海岸", "高台", "丘の上", "坂下", "谷津",
    # 位置・施設系
    "駅前", "駅南", "駅北", "駅東", "駅西", "大通", "中通", "小路", "横町",
    "宮前", "寺前", "神社前", "市役所前", "県庁前",
    # 都市的な町名
    "銀座", "丸の内", "霞が関", "永田町", "赤坂", "六本木", "新宿", "渋谷",
    "池袋", "上野", "浅草", "品川", "目黒", "恵比寿", "表参道", "麻布",
    # その他よくある町名
    "幸町", "栄町", "寿町", "千代田", "富士見", "旭町", "曙町", "春日",
    "文京", "学園", "大学", "学校", "公園", "団地", "住宅", "ニュータウン"
]

# 姓（追加）
SURNAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
    "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
    "山崎", "森", "池田", "橋本", "阿部", "石川", "山下", "中島", "石井", "小川",
    "前田", "藤田", "岡田", "後藤", "長谷川", "村上", "近藤", "石田", "遠藤", "青木",
    "坂本", "斉藤", "福田", "太田", "西村", "藤井", "金子", "中野", "藤原", "原田"
]

# 名（追加）
GIVEN_NAMES = [
    "太郎", "次郎", "三郎", "四郎", "一郎", "健太", "翔太", "優太", "大輝", "陽翔",
    "花子", "美咲", "さくら", "葵", "結衣", "陽菜", "凛", "美月", "愛", "結菜",
    "明", "誠", "武", "勇", "学", "薫", "愛子", "恵", "真理", "由美",
    "隆", "弘", "博", "浩", "正", "修", "幸", "直", "茂", "豊"
]

# 会社名の要素
COMPANY_TYPES = ["株式会社", "有限会社", "合同会社", "一般社団法人"]
COMPANY_WORDS = [
    "総合", "システム", "商事", "工業", "製作所", "産業", "物産", "貿易",
    "サービス", "エンジニアリング", "テクノロジー", "ソリューションズ",
    "コンサルティング", "マネジメント", "プランニング", "デザイン"
]
COMPANY_PREFIXES = [
    "日本", "東京", "大阪", "関西", "関東", "中部", "西日本", "東日本",
    "グローバル", "ユニバーサル", "アドバンス", "プレミアム", "スタンダード"
]

# 番地のバリエーション
def generate_addresses(n=200):
    """住所を生成"""
    addresses = []
    for _ in range(n):
        pref = random.choice(PREFECTURES)

        # 50%の確率で政令指定都市の区を使用
        if random.random() < 0.5:
            city = random.choice(CITIES)
        else:
            # 政令指定都市名 + 区名
            base_cities = ["札幌市", "仙台市", "さいたま市", "千葉市", "横浜市", "川崎市",
                          "相模原市", "新潟市", "静岡市", "浜松市", "名古屋市", "京都市",
                          "大阪市", "堺市", "神戸市", "岡山市", "広島市", "北九州市",
                          "福岡市", "熊本市"]
            city = random.choice(base_cities) + random.choice(CITY_WARDS)

        town = random.choice(TOWNS)
        chome = random.randint(1, 10)
        banchi = random.randint(1, 50)
        go = random.randint(1, 30)

        # いくつかのパターン
        patterns = [
            f"{pref}{city}{town}{chome}丁目{banchi}番{go}号",
            f"{pref}{city}{town}{chome}－{banchi}－{go}",
            f"{pref}{city}{town}{chome}丁目{banchi}－{go}",
            f"{pref}{city}{town}{chome}－{banchi}",
        ]
        addresses.append(random.choice(patterns))

    return addresses

def generate_addresses_with_postal(n=100):
    """郵便番号付き住所を生成"""
    addresses = []
    for _ in range(n):
        postal = f"〒{random.randint(100, 999):03d}-{random.randint(0, 9999):04d}"
        pref = random.choice(PREFECTURES)

        # 50%の確率で政令指定都市の区を使用
        if random.random() < 0.5:
            city = random.choice(CITIES)
        else:
            base_cities = ["札幌市", "仙台市", "さいたま市", "千葉市", "横浜市", "川崎市",
                          "相模原市", "新潟市", "静岡市", "浜松市", "名古屋市", "京都市",
                          "大阪市", "堺市", "神戸市", "岡山市", "広島市", "北九州市",
                          "福岡市", "熊本市"]
            city = random.choice(base_cities) + random.choice(CITY_WARDS)

        town = random.choice(TOWNS)
        chome = random.randint(1, 10)
        banchi = random.randint(1, 50)
        go = random.randint(1, 30)

        addresses.append(f"{postal}　{pref}{city}{town}{chome}－{banchi}－{go}")

    return addresses

def generate_full_names(n=100):
    """フルネームを生成"""
    names = []
    for _ in range(n):
        surname = random.choice(SURNAMES)
        given = random.choice(GIVEN_NAMES)

        patterns = [
            f"{surname}　{given}",
            f"{surname}{given}",
            f"{surname}　{given}　様",
        ]
        names.append(random.choice(patterns))

    return names

def generate_companies(n=100):
    """会社名を生成"""
    companies = []
    for _ in range(n):
        company_type = random.choice(COMPANY_TYPES)

        if random.random() > 0.3:
            prefix = random.choice(COMPANY_PREFIXES)
            word = random.choice(COMPANY_WORDS)
            name = f"{company_type}{prefix}{word}"
        else:
            word = random.choice(COMPANY_WORDS)
            name = f"{company_type}{word}"

        companies.append(name)

    return companies

def generate_phone_numbers(n=50):
    """電話番号を生成"""
    phones = []
    area_codes = ["03", "06", "052", "092", "011", "022", "045", "075"]

    for _ in range(n):
        area = random.choice(area_codes)
        mid = random.randint(1000, 9999)
        last = random.randint(1000, 9999)

        patterns = [
            f"{area}-{mid}-{last}",
            f"電話番号：{area}-{mid}-{last}",
            f"TEL：{area}-{mid}-{last}",
        ]
        phones.append(random.choice(patterns))

    return phones

def generate_dates(n=50):
    """日付を生成（昭和・平成・令和・大正のバリエーション）"""
    dates = []

    for _ in range(n):
        # ランダムに元号を選択（大正は使用頻度が低いため除外）
        era_choice = random.choice(['reiwa', 'heisei', 'showa', 'western'])

        if era_choice == 'reiwa':  # 令和（2019年〜）
            year = random.randint(2020, 2025)
            reiwa_year = year - 2018
            patterns = [
                f"{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"令和{reiwa_year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"{year}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}",
                f"{year}.{random.randint(1, 12)}.{random.randint(1, 28)}",
            ]
        elif era_choice == 'heisei':  # 平成（1989-2019）
            year = random.randint(1990, 2019)
            heisei_year = year - 1988
            patterns = [
                f"{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"平成{heisei_year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"{year}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}",
                f"{year}.{random.randint(1, 12)}.{random.randint(1, 28)}",
            ]
        elif era_choice == 'showa':  # 昭和（1926-1989）
            year = random.randint(1950, 1989)
            showa_year = year - 1925
            patterns = [
                f"{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"昭和{showa_year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"{year}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}",
                f"{year}.{random.randint(1, 12)}.{random.randint(1, 28)}",
            ]
        else:  # 西暦のみ
            year = random.randint(1950, 2025)
            patterns = [
                f"{year}年{random.randint(1, 12)}月{random.randint(1, 28)}日",
                f"{year}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}",
                f"{year}.{random.randint(1, 12)}.{random.randint(1, 28)}",
            ]

        dates.append(random.choice(patterns))

    return dates

def generate_amounts(n=50):
    """金額を生成"""
    amounts = []

    for _ in range(n):
        amount = random.choice([1000, 5000, 10000, 50000, 100000, 500000, 1000000])
        amount += random.randint(-500, 500)

        patterns = [
            f"金額：{amount:,}円",
            f"¥{amount:,}",
            f"{amount:,}円",
            f"合計：{amount:,}円",
        ]
        amounts.append(random.choice(patterns))

    return amounts

def generate_mixed_texts(n=100):
    """住所と名前を組み合わせたテキストを生成"""
    texts = []

    for _ in range(n):
        name = f"{random.choice(SURNAMES)}　{random.choice(GIVEN_NAMES)}"
        pref = random.choice(PREFECTURES)

        # 50%の確率で政令指定都市の区を使用
        if random.random() < 0.5:
            city = random.choice(CITIES)
        else:
            base_cities = ["札幌市", "仙台市", "さいたま市", "千葉市", "横浜市", "川崎市",
                          "相模原市", "新潟市", "静岡市", "浜松市", "名古屋市", "京都市",
                          "大阪市", "堺市", "神戸市", "岡山市", "広島市", "北九州市",
                          "福岡市", "熊本市"]
            city = random.choice(base_cities) + random.choice(CITY_WARDS)

        town = random.choice(TOWNS)
        chome = random.randint(1, 10)
        banchi = random.randint(1, 50)

        text = f"{name}\n{pref}{city}{town}{chome}－{banchi}"
        texts.append(text)

    return texts

def main():
    """メイン処理"""
    print("トレーニングテキストを拡張中...")

    all_texts = []

    # 各種テキストを生成（サンプル数を大幅に増やす）
    all_texts.extend(generate_addresses(500))        # 200 → 500
    all_texts.extend(generate_addresses_with_postal(300))  # 100 → 300
    all_texts.extend(generate_full_names(300))       # 100 → 300
    all_texts.extend(generate_companies(200))        # 100 → 200
    all_texts.extend(generate_phone_numbers(150))    # 50 → 150
    all_texts.extend(generate_dates(150))            # 50 → 150
    # all_texts.extend(generate_amounts(150))        # 価格は除外（¥記号のエンコードエラー）
    all_texts.extend(generate_mixed_texts(300))      # 100 → 300

    # 既存のtraining_texts.txtを読み込む（sourceフォルダから）
    existing_texts = []
    try:
        with open('/workspace/source/training_texts.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    existing_texts.append(line)
        print(f"既存のテキスト: {len(existing_texts)}行")
    except FileNotFoundError:
        print("既存のtraining_texts.txtが見つかりません")

    # 結合してシャッフル
    all_texts = existing_texts + all_texts
    random.shuffle(all_texts)

    # 保存（sourceフォルダに保存）
    output_file = '/workspace/source/training_texts_expanded.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 拡張されたトレーニングテキスト\n")
        f.write(f"# 総行数: {len(all_texts)}\n\n")

        for text in all_texts:
            # 全角ASCII文字を半角に変換（モデルの文字セット対応）
            converted = ''
            for char in text:
                # 全角ASCII範囲（0xFF01-0xFF5E）を半角に変換
                if 0xFF01 <= ord(char) <= 0xFF5E:
                    converted += chr(ord(char) - 0xFEE0)
                elif char == '　':  # 全角スペース
                    converted += ' '
                else:
                    converted += char
            f.write(converted + '\n')

    print(f"\n完了！")
    print(f"元のファイル: {len(existing_texts)}行")
    print(f"追加生成: {len(all_texts) - len(existing_texts)}行")
    print(f"合計: {len(all_texts)}行")
    print(f"出力ファイル: {output_file}")
    print(f"\n次のステップ:")
    print(f"  mv {output_file} /workspace/data/training_texts.txt")

if __name__ == "__main__":
    main()
