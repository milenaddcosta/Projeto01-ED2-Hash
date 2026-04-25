import re
import csv
import math

# --- Normalização e Tokenização ---

def normalizar_texto(caminho_arquivo):
    """
    Lê o arquivo, converte para minúsculas e tokeniza usando Regex 
    para manter apenas letras e acentos. Retorna uma lista de palavras distintas.
    """
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read().lower()
    
    # Regex para capturar palavras com letras e acentos
    # \b garante limites de palavra, [a-zÀ-ÿ]+ captura letras minúsculas e acentuadas
    palavras = re.findall(r'[a-zà-ú]+', conteudo)
    
    # Retornar apenas palavras distintas preservando a ordem de aparecimento (opcional)
    distintas = []
    vistas = set()
    for p in palavras:
        if p not in vistas:
            distintas.append(p)
            vistas.add(p)
    return distintas

# --- Estruturas de Dados (do zero) ---

class LinearBaseline:
    """
    Estrutura Linear Simples (Baseline) usando uma lista interna.
    Implementa put e contains sem usar set/dict.
    """
    def __init__(self):
        self.data = []
        self.comparacoes = 0

    def put(self, key):
        # Como o requisito diz para trabalhar com palavras distintas,
        # assume-se que a filtragem já ocorreu ou que put deve garantir isso.
        if not self.contains(key):
            self.data.append(key)

    def contains(self, key):
        for item in self.data:
            self.comparacoes += 1
            if item == key:
                return True
        return False

    def reset_comparacoes(self):
        self.comparacoes = 0

class HashTable:
    """
    Tabela Hash com Encadeamento Separado.
    Cada bucket é uma lista simples.
    """
    def __init__(self, M, hash_func):
        self.M = M
        self.hash_func = hash_func
        self.table = [[] for _ in range(M)]
        self.n = 0
        self.comparacoes_last_op = 0

    def _hash(self, key):
        # Uso de floorMod (h % M em Python já se comporta como floorMod para positivos)
        return self.hash_func(key) % self.M

    def put(self, key):
        idx = self._hash(key)
        # Verifica se já existe (embora o texto já venha filtrado, é boa prática)
        for item in self.table[idx]:
            if item == key:
                return
        self.table[idx].append(key)
        self.n += 1

    def contains(self, key):
        self.comparacoes_last_op = 0
        idx = self._hash(key)
        for item in self.table[idx]:
            self.comparacoes_last_op += 1
            if item == key:
                return True
        return False

    def get_metrics(self):
        """Calcula n, alpha, histograma e max_bucket."""
        counts = [len(bucket) for bucket in self.table]
        max_b = max(counts) if counts else 0
        alpha = self.n / self.M
        return self.n, alpha, counts, max_b

# --- Funções Hash ---

def h1_sum_ascii(s):
    """H1: Soma dos códigos ASCII (ord) dos caracteres."""
    return sum(ord(c) for c in s)

def h2_weighted_sum(s):
    """H2: Soma ponderada pela posição (i+1) * ord(s[i])."""
    return sum((i + 1) * ord(s[i]) for i, c in enumerate(s))

def h3_polynomial_horner(s):
    """H3: Polinomial (Horner) com R=31."""
    h = 0
    R = 31
    for char in s:
        h = (h * R + ord(char))
    return h

def h4_xor_shift(s):
    """H4: Mistura com XOR/shift."""
    h = 0
    for char in s:
        h ^= (h << 5) + (h >> 2) + ord(char)
    return h

def h_bad_prefix(s):
    """Função 'ruim' proposital: usa apenas o código do primeiro caractere."""
    return ord(s[0]) if s else 0

# --- Experimentos ---

def rodar_experimentos():
    arquivos = ['tale.txt', 'quincas_borba.txt']
    Ms = [97, 100, 997]
    hash_funcs = [
        (h1_sum_ascii, "H1_SumASCII"),
        (h2_weighted_sum, "H2_WeightedSum"),
        (h3_polynomial_horner, "H3_Horner31"),
        (h4_xor_shift, "H4_XORShift"),
        (h_bad_prefix, "H_BadPrefix")
    ]

    resultados = []

    for nome_arq in arquivos:
        print(f"Processando {nome_arq}...")
        try:
            palavras = normalizar_texto(nome_arq)
        except FileNotFoundError:
            print(f"Erro: Arquivo {nome_arq} não encontrado.")
            continue

        # Dividir palavras para teste de sucesso e falha
        # Usaremos as próprias palavras para sucesso
        # Para falha, usaremos as palavras invertidas que não existam no conjunto original
        conjunto_original = set(palavras)
        palavras_falha = []
        for p in palavras:
            invertida = p[::-1] + "xyz" # Garante que não está no texto original
            if invertida not in conjunto_original:
                palavras_falha.append(invertida)
            if len(palavras_falha) >= len(palavras):
                break

        # --- Experimentos com LinearBaseline ---
        lb = LinearBaseline()
        for p in palavras:
            lb.put(p) # put already handles distinct words

        n_lb = len(lb.data)

        # Teste de Sucesso para LinearBaseline
        total_comp_success_lb = 0
        for p in palavras:
            lb.reset_comparacoes()
            lb.contains(p)
            total_comp_success_lb += lb.comparacoes
        avg_comp_success_lb = total_comp_success_lb / n_lb if n_lb else 0

        # Teste de Falha para LinearBaseline
        total_comp_fail_lb = 0
        count_fail_lb = 0
        for p in palavras_falha:
            lb.reset_comparacoes()
            lb.contains(p)
            total_comp_fail_lb += lb.comparacoes
            count_fail_lb += 1
        avg_comp_fail_lb = total_comp_fail_lb / count_fail_lb if count_fail_lb > 0 else 0

        resultados.append({
            'texto': nome_arq,
            'M': 0, # N/A for LinearBaseline, using 0 as placeholder
            'hash_name': "LinearBaseline",
            'n': n_lb,
            'alpha': 0, # N/A for LinearBaseline, using 0 as placeholder
            'max_bucket': 0, # N/A for LinearBaseline, using 0 as placeholder
            'avg_bucket': 0, # N/A for LinearBaseline, using 0 as placeholder
            'total_comp_success': total_comp_success_lb,
            'avg_comp_success': round(avg_comp_success_lb, 4),
            'total_comp_fail': total_comp_fail_lb,
            'avg_comp_fail': round(avg_comp_fail_lb, 4)
        })

        # --- Experimentos com Hash Tables ---
        for M in Ms:
            for func, func_name in hash_funcs:
                ht = HashTable(M, func)
                
                # Inserção
                for p in palavras:
                    ht.put(p)
                
                n, alpha, counts, max_b = ht.get_metrics()
                avg_b = sum(counts) / M
                
                # Teste de Sucesso
                total_comp_success = 0
                for p in palavras:
                    ht.contains(p)
                    total_comp_success += ht.comparacoes_last_op
                avg_comp_success = total_comp_success / len(palavras) if palavras else 0
                
                # Teste de Falha
                total_comp_fail = 0
                count_fail = 0
                for p in palavras_falha:
                    ht.contains(p)
                    total_comp_fail += ht.comparacoes_last_op
                    count_fail += 1
                avg_comp_fail = total_comp_fail / count_fail if count_fail > 0 else 0
                
                resultados.append({
                    'texto': nome_arq,
                    'M': M,
                    'hash_name': func_name,
                    'n': n,
                    'alpha': round(alpha, 4),
                    'max_bucket': max_b,
                    'avg_bucket': round(avg_b, 4),
                    'total_comp_success': total_comp_success,
                    'avg_comp_success': round(avg_comp_success, 4),
                    'total_comp_fail': total_comp_fail,
                    'avg_comp_fail': round(avg_comp_fail, 4)
                })

    # Salvar em CSV
    campos = ['texto', 'M', 'hash_name', 'n', 'alpha', 'max_bucket', 'avg_bucket', 
              'total_comp_success', 'avg_comp_success', 'total_comp_fail', 'avg_comp_fail']
    
    with open('resultados_hash.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=campos)
        writer.writeheader()
        writer.writerows(resultados)
    
    print("Experimentos concluídos. Arquivo 'resultados_hash.csv' gerado.")

if __name__ == "__main__":
    rodar_experimentos()
