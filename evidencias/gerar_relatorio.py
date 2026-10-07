"""Gera o relatório da atividade e uma imagem da saída original do ESLint."""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image as PdfImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "relatorio-test-smells.pdf"
LOG = ROOT / "evidencias" / "eslint-antes.txt"
SCREENSHOT = ROOT / "evidencias" / "eslint-antes.png"


def make_screenshot():
    lines = ["$ npx eslint .", *LOG.read_text().splitlines()]
    font = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 18)
    width = max(1100, max(int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(s, font=font)) for s in lines) + 72)
    height = 72 + len(lines) * 30
    canvas = Image.new("RGB", (width, height), "#15202b")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((10, 10, width - 10, height - 10), radius=14, fill="#101820", outline="#526174", width=2)
    draw.ellipse((30, 29, 43, 42), fill="#fa615b")
    draw.ellipse((51, 29, 64, 42), fill="#fbbf46")
    draw.ellipse((72, 29, 85, 42), fill="#45c36f")
    for index, line in enumerate(lines):
        color = "#ff8585" if "error" in line else "#f4cc75" if "warning" in line else "#e5edf4"
        draw.text((32, 63 + index * 30), line, font=font, fill=color)
    canvas.save(SCREENSHOT)


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", fontName="Helvetica-Bold", fontSize=22, leading=28, textColor=colors.HexColor("#15283b"), spaceAfter=18))
styles.add(ParagraphStyle(name="SectionCustom", fontName="Helvetica-Bold", fontSize=14, leading=19, textColor=colors.HexColor("#176884"), spaceBefore=11, spaceAfter=10))
styles.add(ParagraphStyle(name="BodyCustom", fontName="Helvetica", fontSize=10.4, leading=15, spaceAfter=8))
styles.add(ParagraphStyle(name="CaptionCustom", fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#536474"), spaceAfter=8))
styles.add(ParagraphStyle(name="CoverSmall", fontName="Helvetica", fontSize=12, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#536474")))
styles.add(ParagraphStyle(name="CoverBig", fontName="Helvetica-Bold", fontSize=24, leading=31, alignment=TA_CENTER, textColor=colors.HexColor("#15283b")))
styles.add(ParagraphStyle(name="CodeCustom", fontName="Courier", fontSize=7.8, leading=10.5, backColor=colors.HexColor("#f0f4f7"), borderPadding=9, spaceAfter=8))


def p(value, style="BodyCustom"):
    return Paragraph(value, styles[style])


def code(value):
    return Preformatted(value.strip("\n"), styles["CodeCustom"])


def footer(canvas, document):
    canvas.saveState()
    width, _ = document.pagesize
    canvas.setStrokeColor(colors.HexColor("#c7d4db"))
    canvas.line(2 * cm, 1.65 * cm, width - 2 * cm, 1.65 * cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#647587"))
    canvas.drawString(2 * cm, 1.3 * cm, "Teste de Software  |  Refatoração de Testes e Detecção de Test Smells")
    canvas.drawRightString(width - 2 * cm, 1.3 * cm, str(document.page))
    canvas.restoreState()


def build():
    make_screenshot()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=(21 * cm, 29.7 * cm), rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2.1 * cm)
    nome = os.environ.get("ALUNO_NOME", "Joao Vitor Pedersoli Rajao")
    matricula = os.environ.get("ALUNO_MATRICULA", "[Matrícula a preencher]")
    story = []

    # Página 1: capa.
    story += [Spacer(1, 4.2 * cm), p("DISCIPLINA: TESTE DE SOFTWARE", "CoverSmall"), Spacer(1, 1.3 * cm),
              p("Refatoração de Testes e<br/>Detecção de Test Smells", "CoverBig"), Spacer(1, 2.5 * cm),
              p(f"Aluno(a): {nome}", "CoverSmall"), p(f"Matrícula: {matricula}", "CoverSmall"),
              Spacer(1, 5.5 * cm), p("Relatório de análise, refatoração e validação", "CoverSmall"),
              p("Outubro de 2026", "CoverSmall"), PageBreak()]

    # Página 2: análise manual.
    story += [p("1. Análise dos Test Smells", "TitleCustom"),
              p("O repositório-base contém uma suíte em <b>test/userService.smelly.test.js</b>. Antes da alteração, seus quatro testes ativos passavam e um estava ignorado. A leitura manual encontrou os seguintes problemas:"),
              p("1. Assertivas condicionais e lógica no teste", "SectionCustom"),
              p("O teste de desativação percorre usuários com <b>for</b> e escolhe expectativas com <b>if</b>. Cada execução valida caminhos diferentes no mesmo teste. Uma condição alterada pode impedir que determinada assertiva rode, dando uma falsa sensação de cobertura. O ESLint confirmou três ocorrências de <i>jest/no-conditional-expect</i> nesse bloco."),
              p("2. Eager Test: responsabilidades em um único caso", "SectionCustom"),
              p("O teste “deve criar e buscar um usuário corretamente” valida duas operações, e o teste de desativação cobre usuários comuns e administradores ao mesmo tempo. Quando falham, o nome e a saída não deixam claro qual comportamento regrediu. A versão limpa separa cadastro, busca e cada regra de desativação."),
              p("3. Teste de exceção que pode passar silenciosamente", "SectionCustom"),
              p("O cadastro de menor está dentro de <b>try/catch</b>, mas não há assertiva após o <b>try</b>. Se a função deixar de lançar, o teste termina sem executar qualquer <b>expect</b> e ainda passa. A versão limpa usa <b>toThrow</b>, que falha quando a exceção esperada não ocorre."),
              p("4. Fragilidade e teste desativado", "SectionCustom"),
              p("O relatório original é verificado por uma linha formatada com ID e pontuação exatos: mudanças cosméticas podem quebrar o teste. Já o cenário de lista vazia estava em <b>test.skip</b>, sem proteção ativa. A refatoração verifica informações relevantes do relatório e implementa o caso vazio."),
              p("Observação: o ESLint detecta regras sintáticas configuradas; problemas de foco e assertivas frágeis também exigem revisão humana.", "CaptionCustom"), PageBreak()]

    # Página 3: antes e depois.
    story += [p("2. Processo de refatoração", "TitleCustom"),
              p("Exemplo: o teste original de desativação mistura dois cenários em um laço e decide as expectativas em tempo de execução."),
              p("Antes — trecho do arquivo original", "SectionCustom"),
              code("""for (const user of todosOsUsuarios) {
  const resultado = userService.deactivateUser(user.id);
  if (!user.isAdmin) {
    expect(resultado).toBe(true);
    const usuarioAtualizado = userService.getUserById(user.id);
    expect(usuarioAtualizado.status).toBe('inativo');
  } else {
    expect(resultado).toBe(false);
  }
}"""),
              p("Depois — dois testes focados em Arrange, Act, Assert", "SectionCustom"),
              code("""test('desativa um usuário comum', () => {
  const usuario = userService.createUser('Comum', 'comum@teste.com', 30);
  const desativou = userService.deactivateUser(usuario.id);
  expect(desativou).toBe(true);
  expect(userService.getUserById(usuario.id))
    .toEqual(expect.objectContaining({ status: 'inativo' }));
});

test('mantém ativo um administrador quando a desativação é solicitada', () => {
  const administrador = userService.createUser('Admin', 'admin@teste.com', 40, true);
  const desativou = userService.deactivateUser(administrador.id);
  expect(desativou).toBe(false);
  expect(userService.getUserById(administrador.id))
    .toEqual(expect.objectContaining({ status: 'ativo' }));
});"""),
              p("Cada caso prepara apenas seu usuário, executa uma ação e verifica o resultado e o estado observável. Isso remove o <b>if</b> e o <b>for</b>, torna a falha específica e cobre também a permanência do administrador ativo. Outros cenários limpos exercitam busca inexistente, desativação inexistente, relatório vazio e rejeição de menor."), PageBreak()]

    # Página 4: evidências e conclusão.
    story += [p("3. Relatório da ferramenta e validação", "TitleCustom"),
              p("Primeira execução de <b>npx eslint .</b>, antes de criar o arquivo limpo. A imagem abaixo reproduz a saída capturada em <b>evidencias/eslint-antes.txt</b>."),
              PdfImage(str(SCREENSHOT), width=17 * cm, height=17 * cm * (Image.open(SCREENSHOT).height / Image.open(SCREENSHOT).width)),
              Spacer(1, 0.25 * cm),
              p("A análise automática apontou quatro erros de assertiva condicional e dois avisos do teste desativado. Ela acelerou a localização dos pontos problemáticos, enquanto a análise manual identificou o Eager Test, a fragilidade da formatação e o falso positivo do try/catch."),
              p("Validação final", "SectionCustom"),
              p("<b>npx eslint __tests__/userService.clean.test.js</b>: nenhum erro ou aviso. <b>npm test -- --runInBand</b>: duas suítes passaram; 13 testes passaram e o único teste ignorado continua no arquivo original, preservado conforme o enunciado."),
              p("4. Conclusão", "SectionCustom"),
              p("Testes curtos, com cenários independentes e assertivas obrigatórias, deixam as regressões mais visíveis e reduzem o custo de manutenção. O ESLint oferece uma verificação repetível para certos smells; combinado com revisão humana e execução dos testes, ajuda a manter a suíte confiável ao longo das mudanças no software."),
              p("Fontes: repositório-base https://github.com/CleitonSilvaT/test-smelly; enunciado da atividade fornecido pelo docente.", "CaptionCustom")]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
