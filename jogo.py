import pygame as pg  # biblioteca de criacao de jogos
import sys  # usado para fechar a janela ao final do jogo
import os  # usado para acessar as pastas de imagens
import time  # usado para contabilizar o tempo de jogo
from math import floor  # usado para arrendondar valores (para baixo)
from random import randint  # usado para gerar numeros aleatorios

"""
INFORMAÇÕES:
    - Você ganha o jogo se sobreviver por 40 segundos
    - Você perde o jogo se perder as 3 vidas
"""

# ----------------------------------------------- CONSTANTES ----------------------------------------------------

NOME_DO_JOGO = 'Desvie das Bombas!'
FPS = 120
VELOCIDADE_DO_PERSONAGEM = 15  # quantidade de pixels
DELAY_DA_BOMBA = 0.5  # intervalo de spawn entre cada bomba (em segundos)

TECLA_A = pg.K_a
TECLA_D = pg.K_d
TECLA_R = pg.K_r
TECLA_ESQUERDA = pg.K_LEFT
TECLA_DIREITA = pg.K_RIGHT

COR_AMARELA = (255, 234, 0)
COR_VERMELHA = (230, 0, 0)
COR_PRETA = (20, 20, 20)

# ------------------------------------------- CONFIGURAÇÕES DE TELA ---------------------------------------------

# iniciando a biblioteca pygame
pg.init()

# inicia o modulo de som
pg.mixer.init()

# definindo as dimensões da tela de jogo
tela_info = pg.display.Info()
comprimento_tela = int(tela_info.current_w // 1.15)
largura_tela = int(tela_info.current_h // 1.15)

# definindo o título, o ícone e as dimensoes da tela de jogo
pg.display.set_caption(NOME_DO_JOGO)
pg.display.set_icon(pg.image.load('./imagens/bomba.png'))
tela = pg.display.set_mode((comprimento_tela, largura_tela))

# ----------------------------------------- CARREGANDO IMAGENS --------------------------------------------------

# carregando e mudando o tamanho da imagem da bomba
imagem_bomba = pg.transform.scale(pg.image.load("./imagens/bomba.png"), (80, 100))

# carregando e mudando o tamanho das imagens do cenário
imagem_grama = pg.transform.scale(pg.image.load('./imagens/cenario/grama.png'), (comprimento_tela, largura_tela))
imagem_nuvens = pg.transform.scale(pg.image.load('./imagens/cenario/nuvens.jpg'), (comprimento_tela, largura_tela))

# carregando todas as imagens do personagem em uma lista
imagens_personagem = []
for nome_arquivo in os.listdir('./imagens/personagem'):
    imagem = pg.image.load(f'./imagens/personagem/{nome_arquivo}')
    imagens_personagem.append(imagem)

# carregando e mudando o tamanho do icone de vida do personagem
imagens_vida = []
for nome_arquivo in os.listdir('./imagens/vida'):
    imagem = pg.transform.scale(pg.image.load(f'./imagens/vida/{nome_arquivo}'), (200, 50))
    imagens_vida.append(imagem)

# carregando as imagens da explosao
imagens_explosao = []
for nome_arquivo in os.listdir('./imagens/explosao'):
    imagem = pg.image.load(f'./imagens/explosao/{nome_arquivo}')
    imagens_explosao.append(imagem)

# ---------------------------------- CARREGANDO E CONFIGURANDO AUDIOS -------------------------------------------

# carregando audios
musica = pg.mixer.Sound('./audio/music.mp3')
som_explosao = pg.mixer.Sound('./audio/explosao.mp3')

# configurando audio
musica.set_volume(0.5)

# ----------------------------------------- VARIÁVEIS DO JOGO ---------------------------------------------------

# variavel para iniciar o jogo
pode_comecar = False  # muda para True quando o jogador pressionar qualquer tecla no inicio do jogo

# variaveis da bomba
lista_de_bombas = []  # armazena todas as bombas e os seus contornos
comprimento_bomba = imagem_bomba.get_width()
largura_bomba = imagem_bomba.get_height()
pode_spawnar = True  # define se a bomba pode ser spawnada ou não

# variaveis da explosao
indice_imagem_explosao = 0
ocorrendo_explosao = False  # identifica quando uma explosao estiver acontecendo
ponto_de_colisao = ()  # vai identificar o ponto onde a explosao deve ocorrer

# retangulo que contorna a imagem e auxilia na deteccao de colisao
contorno_bomba = imagem_bomba.get_rect()
contorno_bomba.x = 500
contorno_bomba.y = 500

# variaveis do personagem
indice_imagem_atual = 0
comprimento_personagem = imagens_personagem[0].get_width()
largura_persongem = imagens_personagem[0].get_height()
posicao_x = comprimento_tela // 2 - largura_persongem // 2  # metade da tela
posicao_y = 425  # 425 pixels

# variaveis de movimentação
direcacao = 0  # (0 = parado, 1 = direita, -1 = esquerda)

# variaveis de vida
comprimento_vida = imagens_vida[0].get_width()
largura_vida = imagens_vida[0].get_height()
pos_vida_x = comprimento_tela - comprimento_vida - 20
pos_vida_y = 20
vida_total = 3

# variaveis de texto
font = pg.font.SysFont('Arial', 60, True)
texto_ganhou = font.render('VOCÊ GANHOU!', True, COR_AMARELA)
texto_perdeu = font.render('VOCÊ PERDEU!', True, COR_VERMELHA)
texto_iniciar = font.render('Pressione qualquer tecla!', True, COR_PRETA)

# variaveis do temporizador
tempo_atual = 0  # segundos
tempo_inicial = 0  # é atualizado quando o jogador inicia o jogo


def resetar_jogo():
    global pode_comecar, vida_total, tempo_atual, lista_de_bombas, posicao_x, direcacao
    pode_comecar = False  # esperar o jogador apertar uma tecla para começar
    vida_total = 3  # resetar as vidas
    tempo_atual = 0  # resetar o tempo do jogo
    lista_de_bombas = []  # limpar a lista de bombas
    posicao_x = comprimento_tela // 2 - largura_persongem // 2  # centralizar o personagem
    direcacao = 0  # resetar a direção do movimento
    pg.mixer.music.stop()  # Para a música atual
    pg.mixer.music.play(-1)  # Toca novamente desde o início em loop


# ------------------------------------------- LOOPING PRINCIPAL --------------------------------------------------

# iniciando o jogo
rodando = True
while rodando:
    # definindo o fps do jogo
    pg.time.Clock().tick(FPS)

    # ---------------------------------------------  EVENTOS -----------------------------------------------------

    for event in pg.event.get():
        # se clicou no botão de fechar o jogo
        if event.type == pg.QUIT:
            rodando = False

        # se pressionou uma tecla
        if event.type == pg.KEYDOWN:
            if not pode_comecar:
                pode_comecar = True  # indica que o jogo pode comecar
                tempo_inicial = time.time()  # reseta o temporizador (considera o tempo que passou na tela inicial)

            if event.key in (TECLA_D, TECLA_DIREITA):  # se pressionou D ou a tecla direita
                direcacao += 1
            if event.key in (TECLA_A, TECLA_ESQUERDA):  # se pressionou A ou a tecla esquerda
                direcacao -= 1

                # se soltou a tecla
        if event.type == pg.KEYUP:
            if event.key in (TECLA_D, TECLA_DIREITA):  # se soltou D ou a tecla direita
                direcacao -= 1
            if event.key in (TECLA_A, TECLA_ESQUERDA):  # se soltou A ou a tecla esquerda
                direcacao += 1

    # -------------------------------------- DESENHANDO O CENARIO -------------------------------------------

    # desenhando o cenário
    tela.blit(imagem_nuvens, (0, 0))
    tela.blit(imagem_grama, (0, 0))

    # desenhando o barra de vida
    tela.blit(imagens_vida[vida_total], (pos_vida_x, pos_vida_y))

    # desenhando e posicionando o tempo de duracao do jogo
    tempo_formatado = str(floor(tempo_atual))  # remove as casas decimais e transforma em string
    label_tempo = font.render(tempo_formatado, True, (255, 255, 255))
    pos_tempo_x = comprimento_tela // 2 - label_tempo.get_rect().width // 2  # no meio da tela
    pos_tempo_y = 5
    tela.blit(label_tempo, (pos_tempo_x, pos_tempo_y))

    # ---------------------------- ESPERA PRESSIONAR UMA TECLA PARA INICIAR O JOGO ------------------------------
    if not pode_comecar:
        # pegando as dimensoes do texto
        comprimento_texto = texto_iniciar.get_rect().width
        largura_texto = texto_iniciar.get_rect().height

        # calculando a posicao para posicionar o texto
        pos_x = comprimento_tela // 2 - comprimento_texto // 2
        pos_y = largura_tela // 2 - largura_texto // 2

        # desenhando o texto no centro da tela
        tela.blit(texto_iniciar, (pos_x, pos_y))

        pg.display.flip()  # salvando todas as mudanças na tela de jogo

        pg.mixer.music.load("./audio/music.mp3")  # carrega a musica uma vez
        pg.mixer.music.play(-1)  # toca a musica em loop

        continue  # reinicia o looping principal a partir desse ponto (nao lê as linhas de baixo)

    # ------------------------------------------ VERIFICA SE GANHOU ---------------------------------------------

    # se sobriveu por 40 segundos (GANHOU!)
    if tempo_atual >= 40:
        # pegando as dimensoes do texto
        comprimento_texto = texto_ganhou.get_rect().width
        largura_texto = texto_ganhou.get_rect().height

        # calculando a posicao para posicionar o texto
        pos_x = comprimento_tela // 2 - comprimento_texto // 2
        pos_y = (largura_tela // 2 - largura_texto // 2) - 30

        # desenhando o texto no centro da tela
        tela.blit(texto_ganhou, (pos_x, pos_y))

        # Exibir mensagem para reiniciar
        texto_reiniciar = font.render('Pressione R para reiniciar', True, COR_PRETA)
        pos_reiniciar_x = comprimento_tela // 2 - texto_reiniciar.get_rect().width // 2
        pos_reiniciar_y = pos_y + largura_texto + 20
        tela.blit(texto_reiniciar, (pos_reiniciar_x, pos_reiniciar_y))

        pg.mixer.music.stop()  # Para a música atual

        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == TECLA_R:
                resetar_jogo()
                continue

    # ------------------------------------------- VERIFICA SE PERDEU ---------------------------------------------

    # se perdeu as 3 vidas (PERDEU!)
    elif vida_total == 0:
        # pegando as dimensoes do texto
        comprimento_texto = texto_perdeu.get_rect().width
        largura_texto = texto_perdeu.get_rect().height

        # calculando a posicao para posicionar o texto
        pos_x = comprimento_tela // 2 - comprimento_texto // 2
        pos_y = (largura_tela // 2 - largura_texto // 2) - 30

        # desenhando o texto no centro da tela
        tela.blit(texto_perdeu, (pos_x, pos_y))

        # Exibir mensagem para reiniciar
        texto_reiniciar = font.render('Pressione R para reiniciar', True, COR_PRETA)
        pos_reiniciar_x = comprimento_tela // 2 - texto_reiniciar.get_rect().width // 2
        pos_reiniciar_y = pos_y + largura_texto + 20
        tela.blit(texto_reiniciar, (pos_reiniciar_x, pos_reiniciar_y))

        pg.mixer.music.stop()  # Para a música atual

        for event in pg.event.get():
            if event.type == pg.KEYDOWN and event.key == TECLA_R:
                resetar_jogo()
                continue

    else:
        # --------------------------------- DEFINE A  POSIÇÃO DO PERSONAGEM --------------------------------------

        # definindo a posicao do personagem
        posicao_x += direcacao * VELOCIDADE_DO_PERSONAGEM

        # impedindo o jogador se sair do limite da tela
        if posicao_x < 0:
            posicao_x = 0
        elif posicao_x > comprimento_tela - comprimento_personagem:
            posicao_x = comprimento_tela - comprimento_personagem

        # ------------------------------------- DESENHANDO O PERSONAGEM ------------------------------------------

        # selecionando a imagem do personagem
        imagem_personagem = imagens_personagem[indice_imagem_atual]

        # retangulo que contorna a imagem e auxilia na deteccao de colisao
        contorno_personagem = imagem_personagem.get_rect()
        contorno_personagem.x = posicao_x
        contorno_personagem.y = posicao_y

        # muda de imagem a medida que o personagem se move (inverte caso esteja indo para a esquerda)
        if direcacao != 0:  # se está se movendo
            indice_imagem_atual += 1  # muda pra proxima imagem do personagem

            # caso esteja movendo pra esquerda
            if direcacao < 0:
                imagem_personagem = pg.transform.flip(imagem_personagem, 1, 0)  # inverte a imagem

        else:  # se estiver parado
            indice_imagem_atual = 0  # mostra a primeira imagem (personagem parado)

        # garantindo que o indice da imagem esteja no limite correto
        if indice_imagem_atual > len(imagens_personagem) - 1:
            indice_imagem_atual = 1

        # desenhando o personagem na tela
        tela.blit(imagem_personagem, contorno_personagem)

        # ----------------------------------------- SPAWNANDO AS BOMBAS ------------------------------------------

        # a cada intervalo de spawn
        if tempo_atual % DELAY_DA_BOMBA == 0:
            if pode_spawnar:  # esse "if" cria um delay e evita que várias bombas sejam spawnadas ao mesmo tempo
                pode_spawnar = False

                # definindo a posicao da nova bomba
                nova_pos_x = randint(0, comprimento_tela - comprimento_bomba)
                nova_pos_y = -largura_bomba

                # criando uma cópia da bomba
                nova_bomba = imagem_bomba.copy()

                # atualizando a posicao do contorno do bomba
                contorno_bomba = nova_bomba.get_rect()
                contorno_bomba.x = nova_pos_x
                contorno_bomba.y = nova_pos_y

                # salvando as informacoes da bomba na lista de bombas
                info_bomba = [imagem_bomba, contorno_bomba]
                lista_de_bombas.append(info_bomba)
        else:
            pode_spawnar = True

        # ------------------------------------------ DESENHANDO AS BOMBAS ----------------------------------------

        # verifica se a lista de bombas não está vazia
        if len(lista_de_bombas) > 0:
            for info_bomba in lista_de_bombas:
                imagem_bomba = info_bomba[0]
                contorno_bomba = info_bomba[1]
                tela.blit(imagem_bomba, contorno_bomba)

        # ----------------------------------------- MOVIMENTANDO AS BOMBAS ---------------------------------------

        # verifica se a lista de bombas não está vazia
        if len(lista_de_bombas) > 0:
            for info_bomba in lista_de_bombas:
                contorno_bomba = info_bomba[1]
                contorno_bomba.y += 15  # aumenta em 15 pixels a posicao no eixo y de cada bomba

        # -------------------------------------------- VERIFICANDO COLISAO ----------------------------------------

        # cria uma nova lista eliminando as bombas que colidiram
        lista_bombas_sem_colisao = []

        # para cada bomba na tela
        for info_bomba in lista_de_bombas:
            imagem_bomba = info_bomba[0]
            contorno_bomba = info_bomba[1]

            # verifica se o personagem colidiu com alguma bomba
            colidiu = contorno_personagem.colliderect(contorno_bomba)
            if colidiu:  # se houve colisão
                # toca o audio da explosao
                som_explosao.play()

                # diminui a vida do personagem
                vida_total -= 1
                if vida_total < 0:
                    vida_total = 0

                # salva o ponto onde ocorreu a colisao
                pos_explosao_x = contorno_bomba.x - comprimento_bomba // 2  # centro da bomba no eixo x
                pos_explosao_y = contorno_bomba.y - largura_bomba // 2  # centro da bomba no eixo y
                ponto_de_colisao = (pos_explosao_x, pos_explosao_y)

                # indica quando a animaçao de explosao deve ocorrer
                ocorrendo_explosao = True

            else:  # se nao houve colisao
                # adiciona na lista apenas as bombas que nao colidiram com o personagem
                lista_bombas_sem_colisao.append([imagem_bomba, contorno_bomba])

        # atualiza a lista de bombas para conter apenas as bombas que nao colidiram com o personagem
        lista_de_bombas = lista_bombas_sem_colisao

        # -------------------------------------- DESENHANDO A EXPLOSAO DA BOMBA ---------------------------------

        # verifica se ocorreu uma explosao
        if ocorrendo_explosao:
            tela.blit(imagens_explosao[indice_imagem_explosao], ponto_de_colisao)  # desenha a explosao na tela
            indice_imagem_explosao += 1  # muda pra proxima imagem da bomba

            # se ja atingiu a ultima imagem de explosao (fim da explosao)
            if indice_imagem_explosao > len(imagens_explosao) - 1:
                # reseta variaveis apos o fim da animacao de explosao
                indice_imagem_explosao = 0
                ocorrendo_explosao = False
                ponto_de_colisao = ()

        # ---------------------------- ELIMINA AS BOMBAS QUE CHEGARAM NO LIMITE INFERIOR DA TELA -----------------

        # cria uma nova lista para armazenar os valores filtrados
        bombas_no_limite_da_tela = []

        # percorre a lista de bombas seleciona apenas as bombas que não ultrapassaram o limite inferior da tela
        for info_bomba in lista_de_bombas:
            contorno_bomba = info_bomba[1]
            if contorno_bomba.y < largura_tela + largura_bomba:
                bombas_no_limite_da_tela.append(info_bomba)

        # atualiza a lista de bombas com valores filtrados
        lista_de_bombas = bombas_no_limite_da_tela

        # ------------------------------ ATUALIZANDO O TEMPO E SALVANDO AS ALTERACOES FEITAS NA TELA ---------------

        # atualizando o tempo de duracao do jogo
        tempo_atual = float(f'{(time.time() - tempo_inicial):.1f}')  # considera apenas 1 casa decimal

    # salvando todas as mudanças na tela de jogo
    pg.display.flip()

# fechando a tela de jogo
pg.quit()
sys.exit()