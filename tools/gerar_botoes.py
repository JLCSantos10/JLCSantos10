"""Gera os botoes 3D empilhados (SVG animado) usados no README do perfil.

    python tools/gerar_botoes.py

Para acrescentar ou remover uma tecnologia, edite apenas a lista TECNOLOGIAS
logo abaixo e rode o comando. O logo e baixado automaticamente do
simple-icons e fica guardado em tools/logos.json.

Os arquivos sao escritos em assets/btn-*.svg e a largura da imagem no
README.md e ajustada sozinha.
"""
import json
import os
import re
import urllib.request

BRANCO = "#ffffff"
PRETO = "#1a1a1a"

# =============================================================================
# EDITE DAQUI
# =============================================================================
# (slug do logo em simpleicons.org, cor do botao, cor do logo, rotulo)
#
# Use PRETO como cor do logo quando o fundo for claro (amarelo, lima, branco);
# nos demais casos use BRANCO.
TECNOLOGIAS = [
    ("r",          "#276DC3", BRANCO, "R"),
    ("powerbi",    "#F2C811", PRETO,  "Power BI"),
    ("qgis",       "#589632", BRANCO, "QGIS"),
    ("rstudioide", "#75AADB", BRANCO, "RStudio"),
    ("git",        "#F05032", BRANCO, "Git"),
]

# (arquivo gerado, slug, cor do botao, cor do logo, rotulo)
# Ao acrescentar um contato, lembre de adicionar o <a href> no README tambem.
CONTATOS = [
    ("btn-linkedin.svg", "linkedin", "#0A66C2", BRANCO, "LinkedIn"),
    ("btn-email.svg",    "gmail",    "#EA4335", BRANCO, "E-mail"),
    ("btn-lattes.svg",   "lattes",   "#005B9F", BRANCO, "Curriculo Lattes"),
]

MAX_POR_LINHA = 5   # acima disso o script quebra em varias linhas
# =============================================================================
# ATE AQUI
# =============================================================================

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, os.pardir)
DESTINO = os.path.join(RAIZ, "assets")
CACHE = os.path.join(AQUI, "logos.json")
URL_RAW = "https://raw.githubusercontent.com/JLCSantos10/JLCSantos10/main/assets"

# o powerbi saiu do simple-icons na v12, por isso a v11 fica como reserva
VERSOES = ["13.0.0", "11.14.0"]
PATH_VALIDO = re.compile(r"^[MmLlHhVvCcSsQqTtAaZz0-9eE,.\s+-]+$")


# --- logos -------------------------------------------------------------------
def carregar_cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    return {}


def baixar_logo(slug):
    """Busca o path do logo no simple-icons e valida o conteudo recebido."""
    for versao in VERSOES:
        url = f"https://cdn.jsdelivr.net/npm/simple-icons@{versao}/icons/{slug}.svg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl"})
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status != 200:
                    continue
                texto = r.read(20000).decode("utf-8", "replace")
        except Exception:
            continue

        achados = re.findall(r'\sd="([^"]+)"', texto)
        if len(achados) != 1:
            continue
        d = achados[0].strip()
        if not PATH_VALIDO.match(d) or len(d) > 6000:
            continue
        print(f"  logo '{slug}' baixado (simple-icons {versao})")
        return d

    raise SystemExit(
        f"\nERRO: nao encontrei o logo '{slug}' no simple-icons.\n"
        f"Confira o nome exato em https://simpleicons.org (o slug fica na URL).\n"
        f"Se o logo nao existir la, baixe um SVG qualquer, copie o conteudo do\n"
        f"atributo d=\"...\" e acrescente a mao em tools/logos.json."
    )


def resolver_logos(itens):
    """Garante que todo slug usado tenha um path no cache."""
    cache = carregar_cache()
    faltando = {it[0] for it in itens} - set(cache)
    for slug in sorted(faltando):
        cache[slug] = baixar_logo(slug)
    if faltando:
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"  tools/logos.json atualizado (+{len(faltando)})")
    return cache


# --- geometria ---------------------------------------------------------------
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
AMPLITUDES = [5.0, 4.0, 3.0, 2.2, 1.5]   # menor nas camadas fundas = paralaxe

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


def botao(logos, slug, cor, cor_logo, rotulo, cx, cy, atraso):
    """Um botao: pilha de camadas + logo na face do topo."""
    partes = []
    # de baixo para cima: o SVG pinta em ordem de documento, entao a face do
    # topo (que carrega o logo) precisa ser a ultima a ser desenhada
    for i in reversed(range(CAMADAS)):
        conteudo = (
            '<rect x="-30" y="-30" width="60" height="60" rx="10" '
            'fill="%s" opacity="%.2f"/>' % (cor, OPACIDADES[i])
        )
        if i == 0:
            conteudo += (
                '<path d="%s" fill="%s" transform="scale(1.3) translate(-12,-12)"/>'
                % (logos[slug], cor_logo)
            )
        partes.append(
            '    <g transform="translate(%.1f,%.1f)">'
            '<g class="cam n%d" style="animation-delay:%.2fs">'
            '<g transform="rotate(-30) skewX(25)">%s</g></g></g>'
            % (cx, cy + i * PASSO, i, atraso + i * 0.09, conteudo)
        )
    return '  <g role="img" aria-label="%s"><title>%s</title>\n%s\n  </g>' % (
        rotulo, rotulo, "\n".join(partes),
    )


def svg(largura, altura, corpo):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
        'viewBox="0 0 %.0f %.0f" fill="none">\n%s\n%s\n</svg>\n'
        % (largura, altura, largura, altura, ESTILO, corpo)
    )


def distribuir(itens):
    """Divide a lista em linhas o mais equilibradas possivel."""
    n = len(itens)
    n_linhas = max(1, -(-n // MAX_POR_LINHA))   # divisao arredondando pra cima
    linhas, inicio = [], 0
    for k in range(n_linhas):
        tam = -(-(n - inicio) // (n_linhas - k))
        linhas.append(itens[inicio:inicio + tam])
        inicio += tam
    return linhas


def um_botao(logos, arquivo, slug, cor, cor_logo, rotulo):
    corpo = botao(logos, slug, cor, cor_logo, rotulo,
                  LARGURA_BOTAO / 2, -TOPO_REL, 0.0)
    caminho = os.path.join(DESTINO, arquivo)
    open(caminho, "w", encoding="utf-8").write(
        svg(LARGURA_BOTAO, ALTURA_BOTAO, corpo))
    return caminho


def grade(logos, arquivo, linhas, gap=16, gap_linha=10):
    largura = max(len(ln) * LARGURA_BOTAO + (len(ln) - 1) * gap for ln in linhas)
    altura = len(linhas) * ALTURA_BOTAO + (len(linhas) - 1) * gap_linha
    corpo, n = [], 0
    for li, linha in enumerate(linhas):
        larg_linha = len(linha) * LARGURA_BOTAO + (len(linha) - 1) * gap
        x0 = (largura - larg_linha) / 2
        for ci, (slug, cor, cor_logo, rotulo) in enumerate(linha):
            cx = x0 + ci * (LARGURA_BOTAO + gap) + LARGURA_BOTAO / 2
            cy = li * (ALTURA_BOTAO + gap_linha) - TOPO_REL
            corpo.append(botao(logos, slug, cor, cor_logo, rotulo, cx, cy, n * 0.15))
            n += 1
    caminho = os.path.join(DESTINO, arquivo)
    open(caminho, "w", encoding="utf-8").write(svg(largura, altura, "\n".join(corpo)))
    return caminho, largura


def ajustar_readme(largura):
    """Atualiza a largura da grade de tecnologias no README."""
    caminho = os.path.join(RAIZ, "README.md")
    texto = open(caminho, encoding="utf-8").read()
    padrao = re.compile(
        r'(src="[^"]*btn-tecnologias\.svg"\s*\n\s*alt="[^"]*"\s*\n\s*width=")(\d+)(")'
    )
    novo, trocas = padrao.subn(lambda m: m.group(1) + str(int(largura)) + m.group(3), texto)
    if trocas:
        open(caminho, "w", encoding="utf-8").write(novo)
        print(f'  README.md: width da grade ajustada para {largura:.0f}')
    else:
        print(f'  AVISO: nao achei a tag da grade no README. '
              f'Ajuste a mao para width="{largura:.0f}".')


if __name__ == "__main__":
    os.makedirs(DESTINO, exist_ok=True)
    logos = resolver_logos(
        [(t[0],) for t in TECNOLOGIAS] + [(c[1],) for c in CONTATOS]
    )

    print("\nbotoes de contato:")
    for arquivo, slug, cor, cor_logo, rotulo in CONTATOS:
        p = um_botao(logos, arquivo, slug, cor, cor_logo, rotulo)
        print("  %-20s %5.1f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))

    linhas = distribuir(TECNOLOGIAS)
    caminho, largura = grade(logos, "btn-tecnologias.svg", linhas)
    print("\ngrade de tecnologias (%s):" % " + ".join(str(len(l)) for l in linhas))
    print("  %-20s %5.1f KB" % (os.path.basename(caminho),
                                os.path.getsize(caminho) / 1024))
    ajustar_readme(largura)

    rotulos = ", ".join(t[3] for t in TECNOLOGIAS)
    print("\nSe mudou a lista, atualize tambem o alt= da grade no README:")
    print(f'  alt="{rotulos}"')
    print("\nPor fim, publique:")
    print("  git add -A && git commit -m \"Atualiza os botoes\" && git push")
