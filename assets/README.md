# Assets da Marca

Esta pasta contém as imagens da identidade visual da sua organização.
Os arquivos de imagem **não são versionados** (estão no `.gitignore`).

Para colocar o sistema em funcionamento, adicione seus próprios arquivos
nesta pasta usando os nomes abaixo. O app detecta e aplica automaticamente.

---

## Ícone da janela (titlebar / taskbar / alt-tab)

| Arquivo | Formato | Descrição |
|---|---|---|
| `vidaplena.ico` | ICO (Windows nativo) | Multi-tamanho embutido: 16/32/48/64/128/256 px. Melhor qualidade na titlebar e taskbar do Windows. |
| `icon_16.png` … `icon_256.png` | PNG | Fallback para Linux/Mac (via `iconphoto`). Forneça todos os tamanhos para qualidade ideal. |

> O app tenta `vidaplena.ico` primeiro no Windows. Se não existir, usa os PNGs.
> Se nenhum arquivo existir, usa o ícone padrão do sistema — o app não quebra.

---

## Logos da marca

| Arquivo | Onde é usado | Tamanho |
|---|---|---|
| `logo_transparent_h32.png` | Topbar do app (cabeçalho) | 41×32 px |
| `logo_transparent_h64.png` | Header de relatórios PDF | 83×64 px |
| `logo_transparent_h220.png` | Tela "Sobre" / cards grandes | 284×220 px |
| `logo_transparent_h400.png` | Splash / tela de login | ~517×400 px |
| `logo_transparent.png` | Fonte hi-res (todos os contextos) | ~820×635 px |
| `logo_transparent_light.png` | Versão para fundos claros | mesma proporção |
| `logo_color.png` | PDF impresso (fundo branco) | — |
| `logo_mono.png` | Marca d'água em documentos | — |

> Todos os `logo_transparent_*.png` têm fundo transparente e funcionam em qualquer fundo escuro sem "quadradão".

---

## Fundos do Display de Apresentação

| Arquivo | Tema | Descrição |
|---|---|---|
| `bg_display_dourado.png` | Dourado | Tons sépia/dourados — elegante e atemporal |
| `bg_display_navy.png` | Navy | Azul-marinho — clássico, estilo cinematográfico |
| `bg_display_vinho.png` | Vinho | Vinho profundo — solene, sensação de altar |
| `bg_display_mata.png` | Verde Mata | Verde sóbrio — ministério e celebração |
| `bg_display_roxo.png` | Roxo | Roxo profundo — espiritual, adoração |
| `bg_display_petroleo.png` | Petróleo | Azul-petróleo — contemporâneo e marcante |
| `bg_display_natal.png` | Natal | Tema natalino — vermelho e dourado festivo |
| `bg_display_pascoa.png` | Páscoa | Tema pascal — tons suaves de ressurreição |
| `bg_display_ceia.png` | Ceia | Tema para a Santa Ceia — sóbrio e reverente |
| `bg_display_infantil.png` | Infantil | Tema colorido para o ministério infantil |

O seletor de fundo aparece automaticamente na aba **Apresentação** para
cada tema cujo arquivo existir. Se nenhum arquivo existir, o display usa
preto puro (botão `●`).

Resolução recomendada para fundos de display: **1920×1080 px** (16:9).
O app redimensiona com cover-fit para qualquer resolução de tela.

---

## O que acontece sem os arquivos?

O app **não quebra**. Cada ponto de uso tem um fallback:

- **Ícone da janela** — usa o ícone padrão do sistema operacional
- **Cabeçalho do app** — exibe uma cruz (+) desenhada no lugar da marca
- **Tela de login** — exibe o nome do sistema em texto no lugar do logo
- **Display de apresentação** — fundo preto puro (sem seletor de tema)
- **Relatórios PDF** — exibe apenas o nome da organização em texto

---

## Formato suportado

Use **PNG** com canal alpha para logos transparentes.
Para os fundos do display, PNG sem transparência (fundo preto renderizado).

> Dica: o `logo_transparent_h400.png` é o logo com fundo transparente
> para usar no painel de login (cor `#1b2030`). O coração e o texto
> "flutuam" sobre qualquer cor de fundo.
