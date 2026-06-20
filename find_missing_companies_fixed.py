#!/usr/bin/env python3
import csv
import os
import re
import sys

def normalize_company_name(name):
    """Normalize company name for comparison"""
    # Remove common prefixes and suffixes
    name = name.replace('株式会社', '').replace('株式会社 ', '')
    name = name.replace('合同会社', '').replace('合同会社 ', '')
    name = name.replace('株式会社 東京支店', '').replace(' 東京支店', '')
    name = name.strip()
    
    # Remove common special characters
    name = re.sub(r'[・\-＿＿（）（）\(\)\[\]【】\{\}「」『』＜＞〈〉《\"]', '', name)
    name = name.strip()
    
    return name

def get_processed_companies():
    """Get list of companies that have been processed"""
    processed = set()
    
    # Get all company directories and files
    company_analysis_dir = '/home/openclaw_user/.openclaw/workspace/company_analysis'
    
    for root, dirs, files in os.walk(company_analysis_dir):
        for dir_name in dirs:
            # Normalize directory name for comparison
            normalized = normalize_company_name(dir_name)
            if normalized:
                processed.add(normalized)
        
        # Also check for single .md files (might need restructuring)
        for file_name in files:
            if file_name.endswith('.md') and not file_name.startswith('.'):
                # Get directory name or use file name
                dir_name = os.path.basename(root)
                if dir_name == company_analysis_dir:
                    # This is a single file, use the file name
                    normalized = normalize_company_name(file_name.replace('.md', ''))
                else:
                    normalized = normalize_company_name(dir_name)
                
                if normalized:
                    processed.add(normalized)
    
    return processed

def get_master_companies():
    """Get list of companies from the master CSV"""
    master = set()
    
    # Use the fetched CSV data from web
    csv_data = """SerialNo,CompanyName,Website,Address,Prefecture,BusinessFields,Features,RecruitTags,Email,Phone,Notes,LogoURL
1,アークシステム株式会社,https://www.ark-sys.co.jp/,220-0011　横浜市西区高島2-6-32　横浜東口ウィスポートビル4F,,パッケージソフトウェア、SES,顧客第一、高い技術力、人間尊重,新卒採用 | 中途採用 | インターンシップ | 常駐・派遣,,,新卒採用 | 中途採用 | インターンシップ | 220-0011 横浜市西区高島2-6-32 横浜東口ウィスポートビル4F | パッケージソフトウェア、SES | 顧客第一、高い技術力、人間尊重 |,
2,アーズ総合開発株式会社,http://www.arz.co.jp/,140-0001　東京都品川区北品川3-6-2　品川MSビル8F,東京都,特長,,,,,140-0001 東京都品川区北品川3-6-2 品川MSビル8F |,
3,アーネスト開発株式会社,https://www.earnestdevelopment.co.jp/,230-0075　横浜市鶴見区上の宮1-36-2,,SES,,中途採用,,,中途採用 | 230-0075 横浜市鶴見区上の宮1-36-2 | SES |,
4,アーバン・コーポレーション株式会社,http://urban-web.co.jp/,220-0011　横浜市西区高島1-2-5　横濱ゲートタワー16F,,特長,,,,,220-0011 横浜市西区高島1-2-5 横濱ゲートタワー16F |,
5,アイエスシー株式会社,http://www.isc-net.co.jp,211-0002　川崎市中原区上丸子山王町1-874-5　ユーテムビル2階,,特長,,,,,211-0002 川崎市中原区上丸子山王町1-874-5 ユーテムビル2階 |,
6,株式会社ＩＳＴソフトウェア,http://www.ist-software.co.jp/,144-8721　東京都大田区蒲田5-37-1　ニッセイアロマスクエア13F,東京都,受託開発ソフトウェア、組み込みソフトウェア、パッケージソフトウェア、情報処理サービス、ネットワーク・通信関連、SES、インターネット利用サポート（情報ネットワーク・セキュリティ・サービス）,,新卒採用 | 中途採用 | インターンシップ | 常駐・派遣,,,新卒採用 | 中途採用 | インターンシップ | 144-8721 東京都大田区蒲田5-37-1 ニッセイアロマスクエア13F | 受託開発ソフトウェア、組み込みソフトウェア、パッケージソフトウェア、情報処理サービス、ネットワーク・通信関連、SES、インターネット利用サポート（情報ネットワーク・セキュリティ・サービス） |,
7,株式会社アイキャル,https://www.ical.jp/,221-0844　横浜市神奈川区沢渡1-2　Ｊプロ高島台サウスビル5F,,情報処理サービス,,新卒採用 | 中途採用 | インターンシップ | 常駐・派遣,,,新卒採用 | 中途採用 | インターンシップ | 221-0844 横浜市神奈川区沢渡1-2 Ｊプロ高島台サウスビル5F | 情報処理サービス |,
8,株式会社ＩＣＯＮ,http://www.e-icon.co.jp/,221-0834　横浜市神奈川区台町13-19　三栄ビル3F,,特長,,,,,221-0834 横浜市神奈川区台町13-19 三栄ビル3F |,
9,株式会社アイ・ジー・スクウェア,https://www.igsquare.co.jp/,220-0004　横浜市西区北幸2-10-27　東武立野ビル3F,,情報処理サービス、SES,,新卒採用 | 常駐・派遣,,,新卒採用 | 220-0004 横浜市西区北幸2-10-27 東武立野ビル3F | 情報処理サービス、SES |,
10,アイシス株式会社,http://www.isis.co.jp/,215-0004　川崎市麻生区万福寺1-1-1 新百合ヶ丘シティビルディング3F,,組み込みソフトウェア、パッケージソフトウェア、情報処理サービス、その他の情報サービス、SES,,新卒採用 | 中途採用 | 常駐・派遣,,,新卒採用 | 中途採用 | 215-0004 川崎市麻生区万福寺1-1-1 新百合ヶ丘シティビルディング3F | 組み込みソフトウェア、パッケージソフトウェア、情報処理サービス、その他の情報サービス、SES |,"""
    
    # Parse CSV data
    lines = csv_data.strip().split('\n')
    reader = csv.reader(lines)
    header = next(reader)
    
    for row in reader:
        if len(row) >= 2:
            serial_no = row[0]
            company_name = row[1].strip()
            normalized = normalize_company_name(company_name)
            if normalized:
                master.add((serial_no, normalized, company_name))
    
    # Get more companies from the actual master file if available
    try:
        with open('/home/openclaw_user/.openclaw/workspace/companies.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            
            for row in reader:
                if len(row) >= 2:
                    serial_no = row[0]
                    company_name = row[1].strip()
                    normalized = normalize_company_name(company_name)
                    if normalized:
                        master.add((serial_no, normalized, company_name))
    except FileNotFoundError:
        pass
    
    return sorted(master, key=lambda x: int(x[0]))

def main():
    print("Finding missing companies...")
    
    processed = get_processed_companies()
    master = get_master_companies()
    
    print(f"Total companies in master list: {len(master)}")
    print(f"Total companies processed: {len(processed)}")
    
    missing = []
    for serial_no, normalized, original_name in master:
        if normalized not in processed:
            missing.append((serial_no, normalized, original_name))
    
    print(f"Companies needing research: {len(missing)}")
    
    if missing:
        print("\nFirst 10 missing companies:")
        for i, (serial_no, normalized, original_name) in enumerate(missing[:10]):
            print(f"{i+1}. Serial {serial_no}: {original_name}")
        
        # Write missing companies to file for processing
        with open('/home/openclaw_user/.openclaw/workspace/companies_to_research_next.txt', 'w', encoding='utf-8') as f:
            for serial_no, normalized, original_name in missing:
                f.write(f"{serial_no},{original_name}\n")
        
        print(f"\nMissing companies saved to companies_to_research_next.txt")
    else:
        print("All companies have been processed!")
    
    return len(missing)

if __name__ == "__main__":
    gap = main()
    sys.exit(gap)