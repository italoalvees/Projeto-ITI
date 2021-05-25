from math import floor, ceil
from typing import AnyStr
import time
import timeit

#Iniciar os dois dicionários usados no compressor e descompressor LZW, 
#são utilizados os valores da tabela ASCII como alfabeto inicial.
#No primeiro é utilizado o valor em Bytes para o indice e no segundo isso é invertido

ASCII_para_INT: dict = {i.to_bytes(1, 'big'): i for i in range(256)}
INT_para_ASCII: dict = {i: b for b, i in ASCII_para_INT.items()}


#Função codificar recebe uma mensagem em qualquer formato e o número de bits que serão usados como indices
def codificar(mensagem: AnyStr, tamanhoKbits: int) -> bytes:
    
    if isinstance(mensagem, str):
        mensagem = mensagem.encode()
    
    print('Tamanho Mensagem Descompactada: ', len(mensagem))
    
    
    #Chaves: dicionário inicial / numero_de_chaves: quantidade de valores no dicionário
    #codificado: Vetor vazio que vai receber os valores codificados/ tam_mensagem: variável usada como fim do loop
    # inicio: é usado como variável principal para saber onde se iniciará as combinações, após serem adicionadas no dicionário
    chaves: dict = ASCII_para_INT.copy()
    numero_de_chaves: int = len(chaves)
    codificado: list = []
    inicio: int = 0
    tam_mensagem: int = len(mensagem) + 1
    

    #Corpo principal da função, inicialmente é testado se o dicionário está preenchido para poder reseta-lo,
    #após isso é iniciado um for que irá de 1 até o tam_mensagem - inicio, esse valor corresponde ao tamanho inicial da msg
    #  - onde está o começo das combinações restantes. Dentro desse for é criada a combinação [inicio : inicio + 1], caso esteja no dicionário,
    #é começado um novo loop e incrementado o i, aumentando assim um caractere na combinação, esse loop só para quando acha uma combinação que 
    # não esteja no dicionário, ai é adicionado no dicionário e resetado o while, seu ponto de parada é ao acabar todas os caracteres da msg.
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
    
    #Aqui é concatenado todos os valores codificados e são preenchidos para terem o tamanhoKbits de bits, 
    #formando assim o arquivo final que será armazenado 
    bits: str = ''.join([bin(i)[2:].zfill(tamanhoKbits) for i in codificado])
        
    return int(bits, 2).to_bytes(ceil(len(bits) / 8), 'big')



#Função decodificar recebe uma mensagem em qualquer formato e o número de bits que serão usados como indices
def decodificar(mensagem: AnyStr, tamanhoKbits: int) -> bytes:
    
    if isinstance(mensagem, str):
        mensagem = mensagem.encode()
   
    print('Tamanho Mensagem Compactada: ', len(mensagem)) 

    #Chaves: dicionário inicial / bits: mensagem codificada em bits
    #cn_extended_bytes: quantidade de caracteres existentes na mensagem / bits²: a mensagem colocada em seu tamanho total, eliminando os 0's excedentes
    # mensagem_lista: são retirados os valores codificados no tamanhoKbits, para serem decodificados
    #anterior: a combinação anterior / descodificado: lista final dos valores decodificados/ numero_de_chaves: tamanho do dicionário

    chaves: dict = INT_para_ASCII.copy()
    bits: str = bin(int.from_bytes(mensagem, 'big'))[2:].zfill(len(mensagem) * 8)
    n_extended_bytes: int = floor(len(bits) / tamanhoKbits)
    bits: str = bits[-n_extended_bytes * tamanhoKbits:]
    mensagem_lista: list = [int(bits[ i * tamanhoKbits: (i + 1) * tamanhoKbits], 2)
                            for i in range(n_extended_bytes)]
        
    anterior: bytes = chaves[mensagem_lista[0]]
    descodificado: list = [anterior]
    numero_de_chaves: int = len(chaves)
    


    #Esse é o corpo principal da função, onde são lidas as msgs codificadas uma por uma,
    #primeiro é testado se o dicionário está cheio, o mesmo método que é usado no codificador para que não haja erros,
    # depois é procurado o valor correspondente no dicionário, caso não pertença ao dicionário atual, 
    # é inferido que o valor seja a combinação anterior mais ela mesma. O valor decodificado é adicionado na string final 
    # e é adicionado a combinação dentro do dicionário, e também incrementado a variável de marcação assim como é guardado o valor atual.
    
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

    #Por fim é retornado o arquivo decoficado em bytes.
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
