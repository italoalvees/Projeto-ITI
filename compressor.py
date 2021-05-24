from math import floor, ceil
from typing import AnyStr
import time
import timeit

ASCII_para_INT: dict = {i.to_bytes(1, 'big'): i for i in range(256)}
INT_para_ASCII: dict = {i: b for b, i in ASCII_para_INT.items()}

def codificar(mensagem: AnyStr, tamanhoKbits: int) -> bytes:
    
    if isinstance(mensagem, str):
        mensagem = mensagem.encode()
    
    print('Tamanho Mensagem Descompactada: ', len(mensagem))
    chaves: dict = ASCII_para_INT.copy()
    numero_de_chaves: int = len(chaves)
    codificado: list = []
    inicio: int = 0
    tam_mensagem: int = len(mensagem) + 1
    
    while True:

        if numero_de_chaves >= 2**tamanhoKbits:
            chaves = ASCII_para_INT.copy()
            numero_de_chaves = len(chaves)

        for i in range(1, tam_mensagem - inicio):
            palavra: bytes = mensagem[inicio : inicio + i]

            if palavra not in chaves:
                codificado.append(chaves[palavra[:-1]])
                chaves[palavra] = numero_de_chaves
                inicio += i - 1
                numero_de_chaves += 1
                break
        else:
            codificado.append(chaves[palavra])
            break
    
    bits: str = ''.join([bin(i)[2:].zfill(tamanhoKbits) for i in codificado])
        
    return int(bits, 2).to_bytes(ceil(len(bits) / 8), 'big')


def decodificar(mensagem: AnyStr, tamanhoKbits: int) -> bytes:
    
    if isinstance(mensagem, str):
        mensagem = mensagem.encode()
   
    print('Tamanho Mensagem Compactada: ', len(mensagem)) 

    chaves: dict = INT_para_ASCII.copy()
    bits: str = bin(int.from_bytes(mensagem, 'big'))[2:].zfill(len(mensagem) * 8)
    n_extended_bytes: int = floor(len(bits) / tamanhoKbits)
    bits: str = bits[-n_extended_bytes * tamanhoKbits:]
    mensagem_lista: list = [int(bits[ i * tamanhoKbits: (i + 1) * tamanhoKbits], 2)
                            for i in range(n_extended_bytes)]
        
    anterior: bytes = chaves[mensagem_lista[0]]
    descodificado: list = [anterior]
    numero_de_chaves: int = len(chaves)
    
    for i in mensagem_lista[1:]:

        if numero_de_chaves >= 2**tamanhoKbits:
            chaves = INT_para_ASCII.copy()
            numero_de_chaves = len(chaves)  # 256
        
        try:
            atual: bytes = chaves[i]
        except KeyError:
            atual = anterior + anterior[:1]

        descodificado.append(atual)
        chaves[numero_de_chaves] = anterior + atual[:1]
        anterior = atual
        numero_de_chaves += 1

    return (b''.join(descodificado)).strip()

arquivos = ['video/video.mp4','texto/corpus16MB.txt']    

for tamanho in range(9,17):

    for a in arquivos:

        print("Tamanho do K = ", tamanho)
        print(a)

        inicio = timeit.default_timer()
        #print('inicio = ', inicio)
        with open(a, 'rb') as arquivo_entrada:
            with open( a+str(tamanho)+'.lzw', 'wb+') as arquivo_compactado:
                arquivo_compactado.write(codificar(arquivo_entrada.read(), tamanho))
        fim = timeit.default_timer()
        #print('fim = ', fim)
        print ('duracao compressao: %f' % (fim - inicio))

        inicio = timeit.default_timer()
        #print('inicio descompressao = ', inicio)
        with open(a+str(tamanho)+'.lzw', 'rb') as arquivo_compactado:
            with open( a+ str(tamanho) + '.lzw'+a[-4:], 'wb+') as arquivo_descompactado:
                arquivo_descompactado.write(decodificar(arquivo_compactado.read(), tamanho))
        fim = timeit.default_timer()
        #print('fim descompressao = ', fim)
        print ('duracao descompressao: %f' % (fim - inicio))
