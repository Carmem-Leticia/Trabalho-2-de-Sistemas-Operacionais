import random
import matplotlib.pyplot as plt
from collections import deque
import statistics
import time

#Simulação do conjunto de trabalho
def gerar_sequencia_referencias(num_referencias, num_processos, arquivo_saida):
    referencias = []
    with open(arquivo_saida, 'w') as f:
        f.write("Sequência de Referências de Páginas\n")
        for processo in range(num_processos):
            f.write(f"\nProcesso {processo + 1}:\n")
            tamanho_conjunto = random.randint(5, 20)
            conjunto_trabalho = list(range(tamanho_conjunto))
            duracao_conjunto = random.randint(200, 500)
            refs_por_processo = num_referencias // num_processos
            for _ in range(refs_por_processo):
                if random.random() < 0.8:
                    pagina = random.choice(conjunto_trabalho)
                else:
                    pagina = random.randint(0, 99)
                referencias.append(pagina)
                f.write(f"{pagina} ")
                if random.random() < 1 / duracao_conjunto:
                    tamanho_conjunto = random.randint(5, 20)
                    conjunto_trabalho = list(range(tamanho_conjunto))
            f.write("\n")
    return referencias

#Algoritmo FIFO
def fifo(paginas, num_molduras):
    molduras = []
    faltas = 0
    fila = deque()
    for pagina in paginas:
        if pagina not in molduras:
            faltas += 1
            if len(molduras) < num_molduras:
                molduras.append(pagina)
                fila.append(pagina)
            else:
                pagina_removida = fila.popleft()
                molduras.remove(pagina_removida)
                molduras.append(pagina)
                fila.append(pagina)
    return faltas

#Algoritmo de Envelhecimento
def envelhecimento(paginas, num_molduras):
    molduras = []
    contadores = {}
    faltas = 0
    for pagina in paginas:
        if pagina not in molduras:
            faltas += 1
            if len(molduras) < num_molduras:
                molduras.append(pagina)
                contadores[pagina] = 0
            else:
                min_contador = min(contadores.values())
                for p in molduras:
                    if contadores[p] == min_contador:
                        molduras.remove(p)
                        del contadores[p]
                        break
                molduras.append(pagina)
                contadores[pagina] = 0
        for p in molduras:
            contadores[p] >>= 1
            if p == pagina:
                contadores[p] |= 0x80
    return faltas

def plot_results(processos_resultados, molduras_teste, num_referencias):
    faltas_fifo_total = processos_resultados['total']['fifo']
    faltas_envelhecimento_total = processos_resultados['total']['envelhecimento']

    media_fifo = statistics.mean(faltas_fifo_total)
    var_fifo = statistics.variance(faltas_fifo_total)
    media_aging = statistics.mean(faltas_envelhecimento_total)
    var_aging = statistics.variance(faltas_envelhecimento_total)

    print("\n--- Estatísticas Totais ---")
    print(f"Tamanho total das referências: {num_referencias}")
    print(f"\nFIFO - Média de faltas: {media_fifo:.2f}")
    print(f"FIFO - Variância: {var_fifo:.2f}")
    print(f"\nEnvelhecimento - Média de faltas: {media_aging:.2f}")
    print(f"Envelhecimento - Variância: {var_aging:.2f}")

    # Gráfico FIFO x Envelhecimento
    plt.figure(figsize=(10, 6))
    fifo_k = [(f / num_referencias) * 1000 for f in faltas_fifo_total]
    aging_k = [(f / num_referencias) * 1000 for f in faltas_envelhecimento_total]

    plt.plot(molduras_teste, fifo_k, marker='o', label='FIFO', color='blue')
    plt.plot(molduras_teste, aging_k, marker='s', label='Envelhecimento', color='red')
    plt.xticks(molduras_teste)
    plt.title('Faltas de Página por 1000 Referências (Total)')
    plt.xlabel('Número de Molduras')
    plt.ylabel('Faltas por 1000 Referências')
    plt.grid(True)
    plt.legend()
    plt.savefig('grafico_fifo_vs_aging.png')
    plt.show()
    plt.close()

def main():
    num_referencias = 10000
    num_processos = 5
    arquivo_saida = "referencias.txt"

    print("Digite os números de molduras a testar (inteiros positivos, separados por espaço):")
    try:
        molduras_teste = [int(x) for x in input().strip().split()]
        if not molduras_teste or any(x <= 0 for x in molduras_teste):
            raise ValueError
    except ValueError:
        print("Entrada inválida. Usando valores padrão: [3, 5, 10, 15, 20]")
        molduras_teste = [3, 5, 10, 15, 20]

    print("Gerando sequência de referências")
    referencias = gerar_sequencia_referencias(num_referencias, num_processos, arquivo_saida)
    print(f"Sequência gerada e salva em {arquivo_saida}")

    refs_por_processo = num_referencias // num_processos
    processos_resultados = {i: {'fifo': [], 'envelhecimento': []} for i in range(num_processos)}
    processos_resultados['total'] = {'fifo': [], 'envelhecimento': []}

    print("\nResultados por Processo:")
    for processo in range(num_processos):
        inicio = processo * refs_por_processo
        fim = (processo + 1) * refs_por_processo
        refs_processo = referencias[inicio:fim]
        print(f"\nProcesso {processo + 1}:")
        for num_molduras in molduras_teste:

            t0_fifo = time.time()
            faltas_fifo = fifo(refs_processo, num_molduras)
            t1_fifo = time.time()
            tempo_fifo = t1_fifo - t0_fifo

            t0_aging = time.time()
            faltas_envelhecimento = envelhecimento(refs_processo, num_molduras)
            t1_aging = time.time()
            tempo_aging = t1_aging - t0_aging

            processos_resultados[processo]['fifo'].append(faltas_fifo)
            processos_resultados[processo]['envelhecimento'].append(faltas_envelhecimento)
            print(f"Molduras: {num_molduras}")
            print(f"FIFO - Faltas: {faltas_fifo} ({(faltas_fifo / refs_por_processo) * 1000:.2f} por 1000), Tempo: {tempo_fifo:.6f} s")
            print(f"Envelhecimento - Faltas: {faltas_envelhecimento} ({(faltas_envelhecimento / refs_por_processo) * 1000:.2f} por 1000), Tempo: {tempo_aging:.6f} s")

    print("\nResultados Agregados:")
    for num_molduras in molduras_teste:
        faltas_fifo = fifo(referencias, num_molduras)
        faltas_envelhecimento = envelhecimento(referencias, num_molduras)
        processos_resultados['total']['fifo'].append(faltas_fifo)
        processos_resultados['total']['envelhecimento'].append(faltas_envelhecimento)
        print(f"\nMolduras: {num_molduras}")
        print(f"FIFO - Total: {faltas_fifo} ({(faltas_fifo / num_referencias) * 1000:.2f} por 1000)")
        print(f"Envelhecimento - Total: {faltas_envelhecimento} ({(faltas_envelhecimento / num_referencias) * 1000:.2f} por 1000)")

    print("\nGerando gráfico")
    plot_results(processos_resultados, molduras_teste, num_referencias)
    print("Gráfico salvo como 'grafico_fifo_vs_aging.png'.")

if __name__ == "__main__":
    main()