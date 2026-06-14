import math

def compute_edge_cost(i, j, S, lambda_t):
    """
    Menghitung bobot fungsi biaya adaptif untuk subsekuens S[i:j].
    Mengembalikan biaya terkecil beserta kamus data statistik lengkap.
    """
    block_elements = S[i:j]
    b = len(block_elements)
    
    if b == 0:
        return 0, {}
    
    BLOCK_OVERHEAD = 12 
    M = block_elements[-1] - block_elements[0] + 1 if b > 1 else 1
    
    # estimasi bit hasil kompresi (cost function konvensional)
    space_ef = (b * 2) + b * math.ceil(math.log2(M / b if b < M else 1)) + BLOCK_OVERHEAD
    space_bitmap = M + BLOCK_OVERHEAD
    
    # estimasi time cost (optimasi cost function)
    time_ef = b * 5       
    time_bitmap = 1       
    
    # pertimbangkan beban term (lambda_t)
    cost_ef = (1 - lambda_t) * space_ef + lambda_t * time_ef
    cost_bitmap = (1 - lambda_t) * space_bitmap + lambda_t * time_bitmap
    
    is_bitmap = cost_bitmap < cost_ef
    chosen_format = "Bitmap" if is_bitmap else "Elias-Fano"
    
    stats = {
        "b": b,
        "M": M,
        "space_ef": space_ef,
        "space_bitmap": space_bitmap,
        "time_ef": time_ef,
        "time_bitmap": time_bitmap,
        "cost_ef": cost_ef,
        "cost_bitmap": cost_bitmap,
        "format_terpilih": chosen_format,
        "biaya_final": min(cost_bitmap, cost_ef)
    }
    
    return stats["biaya_final"], stats

# implementasi dynamic programming
def build_adaptive_pef_index(S, lambda_t):
    n = len(S)
    C = [float('inf')] * (n + 1)
    P = [0] * (n + 1)
    chosen_stats = {}  # Menyimpan seluruh metadata perhitungan DP
    
    C[0] = 0  
    
    for j in range(1, n + 1):
        for i in range(0, j):
            edge_cost, stats = compute_edge_cost(i, j, S, lambda_t)
            current_accumulated_cost = C[i] + edge_cost
            
            if current_accumulated_cost < C[j]:
                C[j] = current_accumulated_cost
                P[j] = i
                chosen_stats[(i, j)] = stats
                
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
        stat = chosen_stats.get((start, end))
        final_blocks.append({
            "nomor_blok": idx + 1,
            "rentang_indeks": (start, end - 1),
            "data_docIDs": S[start:end],
            "metrics": stat
        })
        
    return C[n], final_blocks


def print_detailed_report(title, lambda_val, total_cost, blocks):
    """Fungsi pembantu untuk mencetak log audit laporan yang informatif"""
    print("=" * 75)
    print(f" {title.upper()} ")
    print(f" Parameter Kueri Adaptif (lambda_t) : {lambda_val}")
    print(f" Total Akumulasi Biaya Transversal DP: {total_cost:.4f} bit")
    print("=" * 75)
    
    for b in blocks:
        m = b["metrics"]
        print(f"[Blok {b['nomor_blok']}] Rentang Indeks Absolut: {b['rentang_indeks']}")
        print(f"  ├─ Rangkaian Data DocIDs  : {b['data_docIDs']}")
        print(f"  ├─ Karakteristik Fisik    : b = {m['b']} dokumen, M = {m['M']} (Semesta Lokal)")
        print(f"  ├─ Analisis Ruang Memori  : Elias-Fano = {m['space_ef']} bit | Bitmap = {m['space_bitmap']} bit")
        print(f"  ├─ Analisis Penalti Waktu : Elias-Fano = {m['time_ef']}     | Bitmap = {m['time_bitmap']}")
        print(f"  ├─ HASIL KOMPUTASI BIAYA  : Cost_EF    = {m['cost_ef']:.2f}  | Cost_Bitmap = {m['cost_bitmap']:.2f}")
        print(f"  └─ KEPUTUSAN FINAL LAPISAN: >> {m['format_terpilih'].upper()} <<")
        print("-" * 75)
    print("\n")


inverted_list = [3, 25, 48, 72, 95, 118, 140, 165]

# Eksekusi Skenario A (Populer)
cost_a, blocks_a = build_adaptive_pef_index(inverted_list, lambda_t=0.95)
print_detailed_report("Skenario A: Istilah Populer", 0.95, cost_a, blocks_a)

# Eksekusi Skenario B (Langka)
cost_b, blocks_b = build_adaptive_pef_index(inverted_list, lambda_t=0.05)
print_detailed_report("Skenario B: Istilah Langka", 0.05, cost_b, blocks_b)