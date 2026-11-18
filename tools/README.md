# Botões 3D do README

Os botões empilhados do perfil são SVGs gerados por [`gerar_botoes.py`](gerar_botoes.py).
Eles não são escritos à mão: rode o script e os arquivos em `assets/btn-*.svg`
são reescritos.

```bash
python tools/gerar_botoes.py
```

## Acrescentar uma tecnologia

Abra `gerar_botoes.py` e adicione **uma linha** na lista `TECNOLOGIAS`:

```python
TECNOLOGIAS = [
    ("r",          "#276DC3", BRANCO, "R"),
    ("postgresql", "#4479A1", BRANCO, "PostgreSQL"),   # <- nova
]
```

Os quatro valores são:

| Valor | O que é | Onde achar |
| :--- | :--- | :--- |
| `"postgresql"` | o *slug* do logo | em <https://simpleicons.org>, é o que aparece na URL do ícone |
| `"#4479A1"` | a cor do botão | o próprio site do simple-icons mostra a cor oficial da marca |
| `BRANCO` | a cor do logo | use `PRETO` se o fundo for claro (amarelo, lima, branco), `BRANCO` nos demais |
| `"PostgreSQL"` | o rótulo | vira o texto alternativo, lido por leitores de tela |

Rode o script. Ele baixa o logo sozinho, guarda em `logos.json` para não
baixar de novo, refaz a grade e **ajusta a largura da imagem no README**.
Remover é o mesmo caminho: apague a linha e rode.

O script reorganiza as fileiras sozinho. Até 5 botões ficam em fila única;
acima disso ele divide em linhas equilibradas (7 viram 4 + 3). Para mudar
esse limite, altere `MAX_POR_LINHA`.

A única coisa que ele não atualiza é o `alt=` da grade no README — ao final
da execução ele imprime o texto pronto para você colar.

## Acrescentar um contato

Adicione a linha em `CONTATOS` e, no `README.md`, o link correspondente:

```html
<a href="https://exemplo.com/seu-perfil">
  <img src="https://raw.githubusercontent.com/JLCSantos10/JLCSantos10/main/assets/btn-NOVO.svg" width="106" alt="Rótulo" />
</a>
```

O `<a>` é o que torna o botão clicável. Sem ele a imagem é só decoração.

## Publicar

```bash
git add -A && git commit -m "Atualiza os botões" && git push
```

As imagens só aparecem no perfil depois do push: o `raw.githubusercontent`
serve apenas o que já está no repositório.

## Dois detalhes que costumam confundir

**O GitHub guarda cache das imagens.** Ele serve tudo por um proxy chamado
camo. Se você trocar o conteúdo de um arquivo mantendo o mesmo nome, a versão
antiga pode continuar aparecendo por um tempo. Para forçar a atualização na
hora, mude o nome do arquivo ou acrescente `?v=2` no fim da URL.

**O README não executa CSS nem JavaScript.** O sanitizador do GitHub remove
`<style>`, `<script>`, `onclick` e `class`. É por isso que a animação vive
*dentro* do SVG, e por isso não existe efeito de `:hover` — imagem embutida
não recebe evento de mouse. A animação respeita `prefers-reduced-motion`,
ou seja, fica parada para quem configurou o sistema para reduzir movimento.

## Logo que não existe no simple-icons

É o caso do Lattes. Nesses casos, o `d="..."` do traçado é escrito direto em
`logos.json`, com o desenho em uma caixa de 24x24. O script usa o que
encontrar no arquivo antes de tentar baixar qualquer coisa.
