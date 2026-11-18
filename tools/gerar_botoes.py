"""Gera os botoes 3D empilhados (SVG animado) usados no README do perfil.

Uso:  python tools/gerar_botoes.py
Os arquivos sao escritos em assets/btn-*.svg.

Reproduz o visual do CodePen "3D CSS BUTTON" (rotate(-30deg) skew(25deg)),
trocando o :hover + onclick -- que o README do GitHub nao executa -- por
uma animacao de flutuacao em loop declarada dentro do proprio SVG.
"""
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, os.pardir, "assets")

paths = json.load(open(os.path.join(AQUI, "logos.json"), encoding="utf-8"))

# capelo de formatura desenhado a mao (o Lattes nao tem icone no simple-icons)
paths["lattes"] = (
    "M12 3 1 9l11 6 9-4.9V17h2V9L12 3zM5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82z"
)

# --- geometria -------------------------------------------------------------
# o rect 60x60 centrado na origem, sob rotate(-30) skewX(25), resulta numa
# caixa simetrica em torno da origem: +-53.1 x +-34.0
MEIA_L = 53.1
MEIA_A = 34.0
CAMADAS = 5
PASSO = 9        # deslocamento vertical entre camadas
FLUTUA = 5       # amplitude da camada do topo

ALTURA_BOTAO = MEIA_A + FLUTUA + MEIA_A + PASSO * (CAMADAS - 1) + FLUTUA
LARGURA_BOTAO = MEIA_L * 2
TOPO_REL = -(MEIA_A + FLUTUA)      # borda superior relativa ao centro do topo

OPACIDADES = [1.0, 0.55, 0.38, 0.25, 0.15]
AMPLITUDES = [5.0, 4.0, 3.0, 2.2, 1.5]

ESTILO = """  <style>
    .cam { animation-duration: 3.2s; animation-timing-function: ease-in-out;
           animation-iteration-count: infinite; }
%s
    @media (prefers-reduced-motion: reduce) { .cam { animation: none; } }
  </style>""" % "\n".join(
    "    .n%d { animation-name: f%d; }\n"
    "    @keyframes f%d { 0%%, 100%% { transform: translateY(0); } "
    "50%% { transform: translateY(-%.1fpx); } }" % (i, i, i, a)
    for i, a in enumerate(AMPLITUDES)
)


def botao(slug, cor, cor_logo, rotulo, cx, cy, atraso):
    """Um botao: pilha de camadas + logo na face do topo."""
    partes = []
    # de baixo para cima: o SVG pinta em ordem de documento, entao a face do
    # topo (que carrega o logo) precisa ser a ultima a ser desenhada
    for i in reversed(range(CAMADAS)):
        topo = i == 0
        conteudo = (
            '<rect x="-30" y="-30" width="60" height="60" rx="10" '
            'fill="%s" opacity="%.2f"/>' % (cor, OPACIDADES[i])
        )
        if topo:
            conteudo += (
                '<path d="%s" fill="%s" transform="scale(1.3) translate(-12,-12)"/>'
                % (paths[slug], cor_logo)
            )
        partes.append(
            '    <g transform="translate(%.1f,%.1f)">'
            '<g class="cam n%d" style="animation-delay:%.2fs">'
            '<g transform="rotate(-30) skewX(25)">%s</g></g></g>'
            % (cx, cy + i * PASSO, i, atraso + i * 0.09, conteudo)
        )
    return '  <g role="img" aria-label="%s"><title>%s</title>\n%s\n  </g>' % (
        rotulo,
        rotulo,
        "\n".join(partes),
    )


def svg(largura, altura, corpo):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
        'viewBox="0 0 %.0f %.0f" fill="none">\n%s\n%s\n</svg>\n'
        % (largura, altura, largura, altura, ESTILO, corpo)
    )


def um_botao(arquivo, slug, cor, cor_logo, rotulo):
    cx = LARGURA_BOTAO / 2
    cy = -TOPO_REL
    corpo = botao(slug, cor, cor_logo, rotulo, cx, cy, 0.0)
    caminho = os.path.join(DESTINO, arquivo)
    open(caminho, "w", encoding="utf-8").write(
        svg(LARGURA_BOTAO, ALTURA_BOTAO, corpo)
    )
    return caminho


def grade(arquivo, linhas, gap=16, gap_linha=10):
    largura = max(
        len(ln) * LARGURA_BOTAO + (len(ln) - 1) * gap for ln in linhas
    )
    altura = len(linhas) * ALTURA_BOTAO + (len(linhas) - 1) * gap_linha
    corpo, n = [], 0
    for li, linha in enumerate(linhas):
        larg_linha = len(linha) * LARGURA_BOTAO + (len(linha) - 1) * gap
        x0 = (largura - larg_linha) / 2
        for ci, (slug, cor, cor_logo, rotulo) in enumerate(linha):
            cx = x0 + ci * (LARGURA_BOTAO + gap) + LARGURA_BOTAO / 2
            cy = li * (ALTURA_BOTAO + gap_linha) - TOPO_REL
            corpo.append(botao(slug, cor, cor_logo, rotulo, cx, cy, n * 0.15))
            n += 1
    caminho = os.path.join(DESTINO, arquivo)
    open(caminho, "w", encoding="utf-8").write(
        svg(largura, altura, "\n".join(corpo))
    )
    return caminho, largura, altura


BRANCO = "#ffffff"
PRETO = "#1a1a1a"

if __name__ == "__main__":
    gerados = []
    # contato: arquivos separados, cada um embrulhado num <a> no README
    gerados.append(um_botao("btn-linkedin.svg", "linkedin", "#0A66C2", BRANCO, "LinkedIn"))
    gerados.append(um_botao("btn-email.svg", "gmail", "#EA4335", BRANCO, "E-mail"))
    gerados.append(um_botao("btn-lattes.svg", "lattes", "#005B9F", BRANCO, "Curriculo Lattes"))

    # tecnologias: um unico arquivo, 4 + 3
    caminho, larg, alt = grade(
        "btn-tecnologias.svg",
        [
            [
                ("r", "#276DC3", BRANCO, "R"),
                ("python", "#3776AB", BRANCO, "Python"),
                ("powerbi", "#F2C811", PRETO, "Power BI"),
                ("qgis", "#589632", BRANCO, "QGIS"),
            ],
            [
                ("rstudioide", "#75AADB", BRANCO, "RStudio"),
                ("quarto", "#39729E", BRANCO, "Quarto"),
                ("git", "#F05032", BRANCO, "Git"),
            ],
        ],
    )
    gerados.append(caminho)

    for g in gerados:
        print("%-28s %6.1f KB" % (os.path.basename(g), os.path.getsize(g) / 1024))
    print("\nbotao: %.0f x %.0f  |  grade tecnologias: %.0f x %.0f"
          % (LARGURA_BOTAO, ALTURA_BOTAO, larg, alt))
