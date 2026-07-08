import random
import string

ALFABET = string.ascii_lowercase + "'"   # huruf a-z + tanda apostrof (glottal stop khas Bahasa Makassar)

# -------------------------------------------------------------------------
# 1. DATABASE KAMUS BAHASA MAKASSAR (minimal 10 kata) -> silakan ditambah
# -------------------------------------------------------------------------
KAMUS = {
    "balla'":  "rumah",
    "je'ne'":  "air",
    "nganre":  "makan",
    "nginung": "minum",
    "bunting": "kawin / menikah",
    "lompo":   "besar",
    "ca'di":   "kecil",
    "baji'":   "baik / bagus",
    "kamma":   "begitu / seperti ini",
    "battu":   "datang / dari",
    "tabe'":   "permisi",
    "amma":    "ibu",
}


class GeneticDictionary:
    def __init__(self, kamus, pop_size=6, mutation_rate=0.3):
        self.kamus = kamus
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate

        # state algoritma genetika (disimpan supaya bisa ditampilkan
        # kembali lewat menu 4-9 tanpa perlu menjalankan ulang)
        self.target = None
        self.population = []        # populasi awal (generasi ke-0)
        self.fitness_list = []      # fitness populasi awal
        self.probabilities = []
        self.cumulative = []
        self.random_numbers = []
        self.parents = []
        self.children = []
        self.crossover_points = []
        self.mutated = []
        self.mutation_positions = []
        self.new_population = []    # populasi generasi baru (generasi ke-1)
        self.new_fitness_list = []
        self.generation = 0

    # ---------------------------------------------------------------
    # MENU 1 : Tampilkan Kamus
    # ---------------------------------------------------------------
    def tampilkan_kamus(self):
        print("\n=== Kamus Bahasa Makassar ===")
        print(f"{'No':<4}{'Kata (Makassar)':<16}{'Arti (Indonesia)':<25}")
        print("-" * 45)
        for i, (kata, arti) in enumerate(self.kamus.items(), start=1):
            print(f"{i:<4}{kata:<16}{arti:<25}")

    # ---------------------------------------------------------------
    # MENU 2 : Cari Kata (pencarian biasa berdasarkan key/arti)
    # ---------------------------------------------------------------
    def cari_kata(self, kunci):
        kunci = kunci.strip().lower()
        # cari dari kata Makassar -> arti
        if kunci in self.kamus:
            print(f"\n'{kunci}' (Makassar) artinya -> '{self.kamus[kunci]}'")
            return
        # cari dari arti Indonesia -> kata Makassar
        hasil = [k for k, v in self.kamus.items() if kunci in v.lower()]
        if hasil:
            print(f"\nKata Makassar dengan arti mengandung '{kunci}':")
            for k in hasil:
                print(f"  {k} -> {self.kamus[k]}")
        else:
            print(f"\nKata '{kunci}' tidak ditemukan di kamus.")

    # ---------------------------------------------------------------
    # MENU 3 : Jalankan Algoritma Genetika (menjalankan seluruh proses
    #          1 generasi penuh: fitness -> seleksi -> crossover -> mutasi
    #          -> generasi baru). Hasil tiap tahap disimpan agar bisa
    #          dilihat kembali lewat menu 4-9.
    # ---------------------------------------------------------------
    def jalankan_ga(self, target=None):
        if target is None:
            target = random.choice(list(self.kamus.keys()))
        target = target.strip().lower()
        if target not in self.kamus:
            print(f"\nKata '{target}' tidak ada di kamus, pilih salah satu kata kamus.")
            return

        self.generation = 1
        self.target = target
        panjang = len(target)

        # --- 1. Inisialisasi populasi awal (individu = string acak sepanjang target)
        self.population = [
            "".join(random.choice(ALFABET) for _ in range(panjang))
            for _ in range(self.pop_size)
        ]

        # --- 2. Hitung fitness populasi awal
        self.fitness_list = self._hitung_fitness_list(self.population)

        # --- 3. Seleksi Roulette Wheel
        self._seleksi_roulette()

        # --- 4. Crossover (satu titik potong)
        self._crossover()

        # --- 5. Mutasi Gen
        self._mutasi()

        # --- 6. Generasi baru
        self._generasi_baru()

        print(f"\n>> Algoritma Genetika generasi ke-{self.generation} selesai dijalankan.")
        print(f">> Target pencarian : '{self.target}'")
        print(">> Gunakan menu 4-9 untuk melihat detail setiap tahap.")

    # ---------------------------------------------------------------
    # MENU 4 : Tampilkan Populasi
    # ---------------------------------------------------------------
    def tampilkan_populasi(self):
        if not self.population:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        print(f"\n=== Populasi Awal (Generasi ke-{self.generation}) ===")
        print(f"Target : '{self.target}'")
        print(f"{'Individu':<10}{'Kromosom':<15}{'Fitness':<10}")
        print("-" * 35)
        for i, (ind, fit) in enumerate(zip(self.population, self.fitness_list), start=1):
            print(f"I{i:<9}{ind:<15}{fit:<10.3f}")

    # ---------------------------------------------------------------
    # MENU 5 : Hasil Fitness (rincian perhitungan)
    # ---------------------------------------------------------------
    def _hitung_fitness_list(self, population):
        target = self.target
        hasil = []
        for ind in population:
            cocok = sum(1 for a, b in zip(ind, target) if a == b)
            fitness = cocok / len(target)
            hasil.append(fitness)
        return hasil

    def hasil_fitness(self):
        if not self.population:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        target = self.target
        print(f"\n=== Perhitungan Fitness (Target: '{target}') ===")
        print("Fitness_i = jumlah karakter cocok / panjang target\n")
        for i, ind in enumerate(self.population, start=1):
            print(f"Individu I{i} = '{ind}'")
            print(f"{'Posisi':<8}{'Target':<8}{'Individu':<10}{'Cocok?'}")
            cocok_total = 0
            for pos, (t, k) in enumerate(zip(target, ind), start=1):
                cocok = (t == k)
                cocok_total += cocok
                print(f"{pos:<8}{t:<8}{k:<10}{'Ya' if cocok else 'Tidak'}")
            fitness = cocok_total / len(target)
            print(f"Fitness I{i} = {cocok_total}/{len(target)} = {fitness:.3f}\n")

    # ---------------------------------------------------------------
    # MENU 6 : Seleksi Roulette
    # ---------------------------------------------------------------
    def _seleksi_roulette(self):
        total_fitness = sum(self.fitness_list)
        n = len(self.population)

        # probabilitas & kumulatif
        if total_fitness == 0:
            # semua individu sama buruknya -> beri peluang seragam
            self.probabilities = [1 / n] * n
        else:
            self.probabilities = [f / total_fitness for f in self.fitness_list]

        self.cumulative = []
        kum = 0
        for p in self.probabilities:
            kum += p
            self.cumulative.append(kum)

        # bangkitkan bilangan acak r untuk memilih sejumlah pop_size parent
        self.random_numbers = [random.random() for _ in range(n)]
        self.parents = []
        for r in self.random_numbers:
            for i, c in enumerate(self.cumulative):
                batas_bawah = self.cumulative[i - 1] if i > 0 else 0
                if batas_bawah <= r < c or (i == n - 1):
                    self.parents.append(self.population[i])
                    break

    def seleksi_roulette(self):
        if not self.population:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        print(f"\n=== Seleksi Roulette Wheel (Target: '{self.target}') ===")
        print(f"Total fitness populasi = {sum(self.fitness_list):.3f}\n")
        print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval'}")
        print("-" * 55)
        for i in range(len(self.population)):
            bawah = self.cumulative[i - 1] if i > 0 else 0
            print(f"I{i+1:<9}{self.fitness_list[i]:<10.3f}{self.probabilities[i]:<14.3f}"
                  f"{bawah:.3f} - {self.cumulative[i]:.3f}")

        print("\nProses pemilihan (bilangan acak r dibangkitkan untuk tiap slot):")
        for idx, (r, p) in enumerate(zip(self.random_numbers, self.parents), start=1):
            print(f"  r{idx} = {r:.3f}  -> terpilih individu '{p}'")

        print("\nOrang tua (parent) hasil seleksi:")
        for i, p in enumerate(self.parents, start=1):
            print(f"  Parent {i}: {p}")

    # ---------------------------------------------------------------
    # MENU 7 : Cross Over (single-point crossover, berpasangan)
    # ---------------------------------------------------------------
    def _crossover(self):
        self.children = []
        self.crossover_points = []
        parents = self.parents[:]
        if len(parents) % 2 != 0:
            parents.append(random.choice(parents))  # genapkan jika ganjil

        for i in range(0, len(parents), 2):
            p1, p2 = parents[i], parents[i + 1]
            panjang = min(len(p1), len(p2))
            titik = random.randint(1, panjang - 1) if panjang > 1 else 1
            child1 = p1[:titik] + p2[titik:]
            child2 = p2[:titik] + p1[titik:]
            self.crossover_points.append(titik)
            self.children.append(child1)
            self.children.append(child2)

    def cross_over(self):
        if not self.parents:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        print(f"\n=== Crossover (Target: '{self.target}') ===")
        parents = self.parents[:]
        if len(parents) % 2 != 0:
            parents.append(parents[0])
        idx_child = 0
        for i in range(0, len(parents), 2):
            p1, p2 = parents[i], parents[i + 1]
            titik = self.crossover_points[i // 2]
            c1 = self.children[idx_child]
            c2 = self.children[idx_child + 1]
            idx_child += 2
            print(f"Pasangan {i//2 + 1}: titik potong setelah gen ke-{titik}")
            print(f"  Parent 1 : {p1[:titik]} | {p1[titik:]}")
            print(f"  Parent 2 : {p2[:titik]} | {p2[titik:]}")
            print(f"  Child 1  : {p1[:titik]}|{p2[titik:]} = {c1}")
            print(f"  Child 2  : {p2[:titik]}|{p1[titik:]} = {c2}\n")

    # ---------------------------------------------------------------
    # MENU 8 : Mutasi
    # ---------------------------------------------------------------
    def _mutasi(self):
        self.mutated = []
        self.mutation_positions = []
        for child in self.children:
            child_list = list(child)
            if random.random() < self.mutation_rate:
                posisi = random.randint(0, len(child_list) - 1)
                huruf_lama = child_list[posisi]
                huruf_baru = random.choice(ALFABET)
                child_list[posisi] = huruf_baru
                self.mutation_positions.append((posisi + 1, huruf_lama, huruf_baru))
            else:
                self.mutation_positions.append(None)  # tidak dimutasi
            self.mutated.append("".join(child_list))

    def mutasi(self):
        if not self.children:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        print(f"\n=== Mutasi Gen (Target: '{self.target}') "
              f"| peluang mutasi = {self.mutation_rate} ===")
        for i, (anak, mut, hasil) in enumerate(
                zip(self.children, self.mutation_positions, self.mutated), start=1):
            print(f"\nChild {i} sebelum mutasi : {anak}")
            if mut is None:
                print(f"Child {i} tidak mengalami mutasi -> tetap {hasil}")
            else:
                posisi, lama, baru = mut
                print(f"Gen ke-{posisi} dimutasi secara acak: '{lama}' -> '{baru}'")
                print(f"Child {i} setelah mutasi : {hasil}")

    # ---------------------------------------------------------------
    # MENU 9 : Generasi Baru
    # ---------------------------------------------------------------
    def _generasi_baru(self):
        # populasi generasi berikutnya = individu hasil mutasi
        baru = self.mutated[:self.pop_size]
        while len(baru) < self.pop_size:
            baru.append(random.choice(self.mutated))
        self.new_population = baru
        self.new_fitness_list = self._hitung_fitness_list(self.new_population)

    def generasi_baru(self):
        if not self.new_population:
            print("\nJalankan Algoritma Genetika dulu (menu 3).")
            return
        print(f"\n=== Populasi Generasi ke-{self.generation} (setelah evolusi) ===")
        print(f"Target : '{self.target}'")
        print(f"{'Individu':<10}{'Kromosom':<15}{'Fitness':<10}")
        print("-" * 35)
        ditemukan = False
        for i, (ind, fit) in enumerate(zip(self.new_population, self.new_fitness_list), start=1):
            tanda = "  <-- COCOK!" if ind == self.target else ""
            if ind == self.target:
                ditemukan = True
            print(f"I{i:<9}{ind:<15}{fit:<10.3f}{tanda}")

        if ditemukan:
            print(f"\n>> Kata target '{self.target}' berhasil ditemukan pada generasi ini!")
        else:
            best = max(zip(self.new_population, self.new_fitness_list), key=lambda x: x[1])
            print(f"\n>> Kata target belum sama persis. Individu terbaik sejauh ini: "
                  f"'{best[0]}' (fitness {best[1]:.3f})")
            print(">> Jalankan lagi menu 3 untuk melanjutkan ke generasi berikutnya "
                  "(populasi awal akan dibangkitkan ulang secara acak).")


# =========================================================================
# PROGRAM UTAMA (MENU)
# =========================================================================
def tampilkan_menu():
    print("\n" + "=" * 45)
    print("   === Kamus Bahasa Daerah (Makassar) ===")
    print("=" * 45)
    print("1. Tampilkan Kamus")
    print("2. Cari Kata")
    print("3. Jalankan Algoritma Genetika")
    print("4. Tampilkan Populasi")
    print("5. Hasil Fitness")
    print("6. Seleksi Roulette")
    print("7. Cross Over")
    print("8. Mutasi")
    print("9. Generasi Baru")
    print("10. Keluar")


def main():
    ga = GeneticDictionary(KAMUS, pop_size=6, mutation_rate=0.3)

    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-10): ").strip()

        if pilihan == "1":
            ga.tampilkan_kamus()
        elif pilihan == "2":
            kunci = input("Masukkan kata yang ingin dicari (Makassar / Indonesia): ")
            ga.cari_kata(kunci)
        elif pilihan == "3":
            ga.tampilkan_kamus()
            target = input(
                "\nMasukkan kata target dari kamus di atas (kosongkan untuk acak): "
            ).strip()
            ga.jalankan_ga(target if target else None)
        elif pilihan == "4":
            ga.tampilkan_populasi()
        elif pilihan == "5":
            ga.hasil_fitness()
        elif pilihan == "6":
            ga.seleksi_roulette()
        elif pilihan == "7":
            ga.cross_over()
        elif pilihan == "8":
            ga.mutasi()
        elif pilihan == "9":
            ga.generasi_baru()
        elif pilihan == "10":
            print("\nTerima kasih. Program selesai.")
            break
        else:
            print("\nPilihan tidak valid, silakan pilih 1-10.")


if __name__ == "__main__":
    main()

