# Validação da primeira base

## Executado

Testes locais de Python e Node, preparação repetida em árvore sintética e geração
do XPI opcional. Consultados o código e a documentação oficial da Mozilla para
branding, empacotamento Windows e WebExtensions.

## Ainda necessário

- Compilar a revisão fixada do Firefox com a camada Rechteck em MozillaBuild.
- Instalar o EXE em uma máquina de teste Windows x64 e verificar desinstalação.
- Confirmar que o diretório de perfis não interfere no Firefox instalado.
- Testar navegação HTTPS, certificados, downloads, vídeo e isolamento de processos.
- Instalar uma WebExtension assinada do AMO, revisar permissões, atualizar e remover.
- Testar a extensão Ordnung Start em Gecko, incluindo persistência das anotações.
- Validar interface, foco de teclado, alto contraste e escalas de tela.
- Validar pacote de idioma pt-BR e branding em telas internas e instalador.
- Implementar atualizações próprias e assinatura de código antes de uma release estável.

Não existe resultado de compilação completa nesta entrega. Testes locais não
certificam compatibilidade binária, instalação ou todas as extensões do Firefox.
