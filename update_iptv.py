import requests
import concurrent.futures
import os

def check_url(entry):
    extinf, url = entry
    try:
        # Zaman aşımını 5 saniye olarak ayarlıyoruz
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return extinf, url
    except:
        pass
    return None

def main():
    input_file = 'turkish_channels.m3u'
    output_file = 'turkish_channels.m3u' # Aynı dosyayı güncelleyeceğiz
    
    if not os.path.exists(input_file):
        print(f"Hata: {input_file} bulunamadı.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    header = lines[0] if lines[0].startswith('#EXTM3U') else '#EXTM3U\n'
    
    for i in range(len(lines)):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines):
                entries.append((lines[i], lines[i+1].strip()))

    print(f"Toplam {len(entries)} bağlantı kontrol ediliyor...")
    
    # GitHub Actions ortamında çok fazla kaynak tüketmemek için worker sayısını dengeli tutuyoruz
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_url, entries))
        
    working_entries = [r for r in results if r is not None]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(header)
        for extinf, url in working_entries:
            f.write(extinf)
            f.write(url + '\n')
            
    print(f"Kontrol tamamlandı. {len(entries)} bağlantıdan {len(working_entries)} tanesi aktif kalarak güncellendi.")

if __name__ == "__main__":
    main()
