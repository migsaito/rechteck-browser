# RECHTECK BROWSER

guten tag. gecko. ordnung.

Projeto de navegador desktop baseado no código do Firefox, com o motor **Gecko**
e as **WebExtensions do Firefox**. O formato escolhido para Windows x64 é um
**instalador completo EXE**, produzido pelo empacotador NSIS da Mozilla.

## Estado real

Esta primeira versão contém uma camada de código aplicável ao Firefox, identidade
visual, scripts de preparação/compilação/empacotamento e uma extensão opcional.
O enorme código de Gecko e Firefox fica no repositório upstream, fixado em
`upstream.json`, e é compilado junto com esta camada.

**Ainda não há navegador compilado, instalador testado ou release pronta para uso.**
Os testes deste repositório verificam scripts e regras da extensão, não substituem
uma compilação completa nem testes de navegação. O snapshot atual é de desenvolvimento,
proveniente de mozilla-central. Atualize a revisão e valide antes de distribuir.

## O que o código faz

- Mantém o navegador completo do Firefox: abas, histórico, favoritos, downloads,
  ferramentas de desenvolvimento e gerenciador de extensões.
- Gera uma marca retangular original e altera nomes da aplicação e do instalador.
- Aplica cantos retos à interface do navegador sem alterar as páginas visitadas.
- Usa diretório de dados `Rechteck` e identidade de comunicação própria.
- Define português brasileiro como idioma preferido das páginas. A interface da
  primeira compilação é en-US; um pacote de idioma pt-BR precisa de teste adicional.
- Preserva APIs, permissões e verificações de assinatura das extensões upstream.
- Compila a partir do código-fonte completo, sem Chromium ou Electron.

O nome interno do executável nesta primeira versão continua sendo `firefox.exe`.
O nome exibido e o instalador são Rechteck Browser. Renomear o binário e todos os
registros associados é uma etapa futura, não um arquivo renomeado artificialmente.

## Compilar no Windows

Use Windows x64, MozillaBuild e um checkout preparado conforme o
[guia oficial da Mozilla](https://firefox-source-docs.mozilla.org/setup/windows_build.html).
O upstream recomenda pelo menos 40 GB livres. Os caminhos de compilação não devem
conter espaços. Escolha a compilação completa de Firefox no bootstrap, não Artifact Mode.

Na shell do MozillaBuild, supondo que o Firefox já foi baixado e preparado pelo bootstrap:

```bash
git clone https://github.com/migsaito/rechteck-browser.git /c/rechteck-browser
cd /c/mozilla-source/firefox
git fetch origin 54145f37844018dee93406811dcdeeba00689022
git checkout --detach 54145f37844018dee93406811dcdeeba00689022
cd /c/rechteck-browser
python3 scripts/prepare.py /c/mozilla-source/firefox --dry-run
bash scripts/build-windows.sh /c/mozilla-source/firefox
```

Se o bootstrap criou um `mozconfig`, guarde esse arquivo fora do checkout antes
de executar a preparação: o script recusa sobrescrever uma configuração diferente.
Use um checkout dedicado, pois a preparação altera preferências e CSS upstream.
Ela verifica a revisão, conserva os arquivos originais de branding e pode ser
reexecutada sem duplicar suas alterações.

O script chama `mach build`, `mach package` e o alvo `installer`. Só após esses passos
terminarem ele coleta o EXE produzido, seu SHA-256 e a revisão usada em `dist/`.
O coletor falha se não encontrar exatamente um instalador, sem gerar um EXE fictício.

Saída esperada após uma compilação bem-sucedida:

```text
dist/Rechteck-Browser-Setup.exe
dist/SHA256SUMS
dist/build-info.json
```

Esta configuração desativa o atualizador e o serviço de manutenção da Mozilla,
pois ainda não existe infraestrutura própria de atualizações. Atualizações do navegador
serão manuais nesta fase. O EXE de desenvolvimento não tem assinatura digital.
Antes de lançar uma versão, validar instalação, desinstalação, perfis separados,
certificados, sandbox, navegação e extensões; definir distribuição e atualização próprias.

## Extensões

Use `Ctrl+Shift+A` ou `about:addons` para gerenciar extensões. O catálogo pretendido
é [Firefox Add-ons](https://addons.mozilla.org/pt-BR/firefox/). A compatibilidade depende
das APIs e versões suportadas pelo upstream; não prometemos funcionamento de todas
as extensões. Pacotes CRX da Chrome Web Store não são instaláveis diretamente.

`extensions/ordnung-start` é uma WebExtension Manifest V3 opcional e original,
com nova aba, atalhos, pesquisa no DuckDuckGo e anotações em armazenamento local.
Não solicita leitura do histórico nem acesso às páginas. A pesquisa digitada é enviada
ao DuckDuckGo quando o usuário a envia; as anotações não são enviadas a um servidor.

Para testá-la no Firefox ou no Rechteck compilado:

1. Abra `about:debugging#/runtime/this-firefox`.
2. Escolha carregar extensão temporária e selecione seu `manifest.json`.
3. Abra uma nova aba e teste pesquisa, endereços e anotações.

Essa instalação é temporária. Para distribuição permanente, enviar a extensão para
assinatura no AMO. O projeto não desativa a verificação de assinaturas.
Para gerar um pacote de teste sem assinatura:

```bash
python3 scripts/package-extension.py
```

## Testes rápidos

Sem dependências adicionais, com Python 3.10+ e Node.js 22+:

```bash
python3 -m unittest discover -s tests -v
node --test tests/destination.test.mjs
```

Os testes de preparação usam uma árvore sintética: verificam idempotência,
proteção de configurações existentes, branding e coleta de artefatos. O teste de
destinos verifica pesquisa, HTTPS e rejeição de URLs executáveis e credenciais.

## Licenças e fontes

O código original deste repositório usa MIT, conforme `LICENSE`. Firefox e Gecko
mantêm suas licenças upstream, incluindo MPL-2.0. Arquivos upstream modificados
continuam sujeitos às licenças originais; MIT não relicencia o navegador inteiro.
Distribuições devem incluir os avisos upstream e disponibilizar o código-fonte
correspondente às modificações, com revisão e scripts de compilação.

- [Código upstream Firefox](https://github.com/mozilla-firefox/firefox)
- [Branding da Mozilla](https://firefox-source-docs.mozilla.org/browser/branding/docs/index.html)
- [Instalador Windows](https://firefox-source-docs.mozilla.org/browser/installer/windows/installer/InstallerBuild.html)
- [WebExtensions](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions)

MSI fica para uma etapa futura de distribuição corporativa. Nesta versão, EXE.
