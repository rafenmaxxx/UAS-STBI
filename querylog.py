import math
import time

def compute_edge_cost(i, j, S, lambda_t):
    block_elements = S[i:j]
    b = len(block_elements)
    if b == 0: return 0, "Empty"
    
    # bit untuk tingkat pertama PEF
    BLOCK_OVERHEAD = 12 
    
    M = block_elements[-1] - block_elements[0] + 1 if b > 1 else 1
    
    # estimasi biaya ruang w(i,j) + overhead
    space_ef = (b * 2) + b * math.ceil(math.log2(M / b if b < M else 1)) + BLOCK_OVERHEAD
    space_bitmap = M + BLOCK_OVERHEAD
    
    # estimasi time cost
    time_ef = b * 5       
    time_bitmap = 1       
    
    cost_ef = (1 - lambda_t) * space_ef + lambda_t * time_ef
    cost_bitmap = (1 - lambda_t) * space_bitmap + lambda_t * time_bitmap
    
    if cost_bitmap < cost_ef:
        return cost_bitmap, "Bitmap"
    else:
        return cost_ef, "Elias-Fano"

# implementasi dynamic programming
def build_pef_index(S, lambda_t):
    n = len(S)
    C = [float('inf')] * (n + 1)
    P = [0] * (n + 1)
    chosen_formats = {}
    C[0] = 0
    
    for j in range(1, n + 1):
        for i in range(0, j):
            edge_cost, block_type = compute_edge_cost(i, j, S, lambda_t)
            current_accumulated_cost = C[i] + edge_cost
            if current_accumulated_cost < C[j]:
                C[j] = current_accumulated_cost
                P[j] = i
                chosen_formats[(i, j)] = block_type
                
    boundaries = []
    current_node = n
    while current_node > 0:
        boundaries.append(current_node)
        current_node = P[current_node]
    boundaries.append(0)
    boundaries.reverse()
    
    final_blocks = []
    for idx in range(len(boundaries) - 1):
        start = boundaries[idx]
        end = boundaries[idx + 1]
        final_blocks.append(chosen_formats.get((start, end)))
        
    return final_blocks

def hitung_lambda(term, log_data):
    """Menghitung nilai lambda_t secara dinamis berdasarkan rasio trafik"""
    total_trafik = sum(log_data.values())
    # normalisasi
    return log_data[term] / total_trafik

def cetak_dashboard_sistem(iterasi_ke, kueri_terakhir):
    print(f"\n" + "="*65)
    print(f" ITERASI KE-{iterasi_ke} | Kueri Masuk Baru: '{kueri_terakhir}'")
    print("="*65)
    
    print(f"{'TERM':<12} | {'FREKUENSI LOG':<15} | {'NILAI LAMBDA (λ_t)':<20}")
    print("-" * 65)
    for term in query_log:
        lambda_t = hitung_lambda(term, query_log)
        print(f"{term:<12} | {query_log[term]:<15} | {lambda_t:<20.4f}")
    
    print("\n" + "."*65)
    
    print(" tingkat kedua PEF:")
    print("-" * 65)
    for term, posting_list in inverted_index_db.items():
        lambda_t = hitung_lambda(term, query_log)
        
        # jalankan dynamic programming untuk update inverted list
        struktur_blok = build_pef_index(posting_list, lambda_t)
        
        print(f"Term '{term}':")
        print(f"  └─ Data DocIDs : {posting_list}")
        print(f"  └─ Format Blok : {struktur_blok}")
    print("="*65 + "\n")

# inisialisasi
# inverted index
inverted_index_db = {
    "itb": [3, 5, 7, 15, 16, 18, 19, 22],
    "stbi": [1, 2, 5, 9, 12, 15],
    "arkebuse": [4, 11, 20]
}

# query log
query_log = { "itb": 1, "stbi": 1, "arkebuse": 1 }

# iterasi awal
cetak_dashboard_sistem(iterasi_ke=0, kueri_terakhir="-")
time.sleep(2)

# iterasi #1: tambah query itb
for _ in range(5): query_log["itb"] += 1
cetak_dashboard_sistem(iterasi_ke=1, kueri_terakhir="itb (x5)")
time.sleep(2)

# iterasi #2: tambah query stbi
for _ in range(5): query_log["stbi"] += 1
cetak_dashboard_sistem(iterasi_ke=2, kueri_terakhir="stbi (x5)")
time.sleep(2)

# iterasi #3: tambah query arkebuse secara signifikan
for _ in range(25): query_log["arkebuse"] += 1
cetak_dashboard_sistem(iterasi_ke=3, kueri_terakhir="arkebuse (x25)")
time.sleep(2)

# iterasi #4: tambah query itb secara signifikan -> kecilkan stbi
for _ in range(25): query_log["itb"] += 1
cetak_dashboard_sistem(iterasi_ke=4, kueri_terakhir="itb (x25)")
time.sleep(2)
