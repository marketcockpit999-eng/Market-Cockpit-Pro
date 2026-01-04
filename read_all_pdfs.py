import PyPDF2
import os

pdf_files = [
    'AI投資バブルと金融市場予測.pdf',
    'ハセットFRB議長と債券市場の衝突.pdf',
    '投資戦略と将来価格予測.pdf',
    '未来予測レポート：流動性、AI、アバンダンス.pdf',
    '未来予測：中国・EU・地政学と円安.pdf',
    '未来資産シミュレーション：2040年まで.pdf',
    '米国経済長期予測：財政・金融・ドル覇権.pdf',
]

output = []
for pdf_file in pdf_files:
    if os.path.exists(pdf_file):
        try:
            with open(pdf_file, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    # Join single characters that were split
                    text += page_text.replace('\n', '')
                
                # Add proper line breaks at sentences
                text = text.replace('。', '。\n')
                text = text.replace('：', '：\n')
                
                output.append(f"\n{'='*60}\n📄 {pdf_file}\n{'='*60}\n{text[:10000]}")
        except Exception as e:
            output.append(f"\n{pdf_file}: ERROR - {e}")

with open('all_reports_clean.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Done! Saved to all_reports_clean.txt")
