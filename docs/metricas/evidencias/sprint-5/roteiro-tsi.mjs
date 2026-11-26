// Ciclo 1 do roteiro de sistema (TSI-01 a TSI-04), Quadro 26 da Visão v2.7.
// Executa as jornadas no navegador e salva capturas de tela como evidência.
import { chromium } from 'playwright-core'
import fs from 'node:fs'

const BASE = process.env.BASE ?? 'http://localhost:8080'
const OUT = process.argv[2]
fs.mkdirSync(OUT, { recursive: true })
const stamp = Date.now()
const log = []
const note = (caso, msg) => { log.push(`${caso}: ${msg}`); console.log(`${caso}: ${msg}`) }

const browser = await chromium.launch({ channel: 'chrome', headless: true })
const shot = (page, nome) => page.screenshot({ path: `${OUT}/${nome}.png`, fullPage: true })

async function cadastrarELogar(page, email, senha, prefixo) {
  await page.goto(`${BASE}/cadastro`)
  await page.getByLabel('E-mail').fill(email)
  await page.getByLabel('Senha', { exact: true }).fill(senha)
  await page.getByLabel('Confirme a senha').fill(senha)
  const boxes = page.locator('input[type=checkbox]')
  await boxes.nth(0).check()
  await boxes.nth(1).check()
  await shot(page, `${prefixo}-01-cadastro`)
  await page.getByRole('button', { name: 'Criar conta' }).click()
  await page.waitForTimeout(1500)
  if (page.url().includes('/login')) {
    await shot(page, `${prefixo}-02-pos-cadastro`)
    await page.getByLabel('E-mail').fill(email)
    await page.getByLabel('Senha').fill(senha)
    await page.getByRole('button', { name: 'Entrar' }).click()
    await page.waitForTimeout(1500)
  }
  await shot(page, `${prefixo}-03-logado`)
  note(prefixo, `após cadastro/login a URL é ${page.url()}`)
}

async function fazerCheckin(page, respostas, prefixo) {
  await page.goto(`${BASE}/dailycheckin`)
  await page.waitForSelector('#checkin-title')
  const selects = page.locator('form select')
  for (let i = 0; i < respostas.length; i++) {
    if (respostas[i] !== null) await selects.nth(i).selectOption({ label: respostas[i] })
  }
  await shot(page, `${prefixo}-04-checkin-preenchido`)
  const respPromise = page.waitForResponse((r) => r.url().endsWith('/api/checkins') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Enviar check-in' }).click()
  const resp = await respPromise
  const corpo = await resp.json()
  note(prefixo, `POST /api/checkins → ${resp.status()} ${JSON.stringify(corpo)}`)
  await page.waitForTimeout(1500)
  await shot(page, `${prefixo}-05-apos-checkin`)
  note(prefixo, `após o envio a URL é ${page.url()}`)
  return corpo
}

// TSI-04: Ajuda Imediata sem login.
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  await page.goto(`${BASE}/login`)
  const botao = page.getByRole('link', { name: /Preciso de ajuda agora/ })
  note('TSI-04', `botão visível na tela de login: ${await botao.isVisible()}`)
  await shot(page, 'tsi04-01-login-sem-sessao')
  await botao.click()
  await page.waitForTimeout(800)
  const texto = await page.locator('main').innerText()
  note('TSI-04', `URL após clicar: ${page.url()}; CVV 188: ${texto.includes('188')}; SAMU 192: ${texto.includes('192')}`)
  await shot(page, 'tsi04-02-tela-ajuda')
  await ctx.close()
}

// TSI-01: jornada principal do check-in (P1 = 2, demais favoráveis).
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  const email = `tsi01-${stamp}@exemplo.com`
  await cadastrarELogar(page, email, 'SenhaTeste123', 'tsi01')
  const corpo = await fazerCheckin(page, ['Ruim', 'Nada', 'Muito bom', 'Nada', 'Não'], 'tsi01')
  const texto = await page.locator('main').innerText()
  const titulos = (corpo.recomendacoes ?? []).map((r) => r.titulo)
  note('TSI-01', `materiais da resposta exibidos na tela: ${titulos.map((t) => `${t}=${texto.includes(t)}`).join(', ') || '(nenhum na resposta)'}`)
  const resumo = page.getByText('Por que estou vendo isto?')
  if (await resumo.count()) {
    await resumo.first().click()
    await page.waitForTimeout(300)
    await shot(page, 'tsi01-05b-motivo-aberto')
  }
  const textoMotivo = await page.locator('main').innerText()
  note('TSI-01', `motivo exibido: ${(corpo.recomendacoes ?? []).some((r) => textoMotivo.includes(r.motivo))}`)
  const link = page.getByRole('link', { name: /Abrir no site oficial/ })
  if (await link.count()) {
    note('TSI-01', `href do link: ${await link.first().getAttribute('href')}; target=${await link.first().getAttribute('target')}`)
    const [aba] = await Promise.all([page.context().waitForEvent('page'), link.first().click()])
    const resp = await aba.waitForLoadState('domcontentloaded', { timeout: 30000 }).then(() => null).catch((e) => e)
    await aba.waitForTimeout(2000)
    note('TSI-01', `nova aba abriu em ${aba.url()}; título "${await aba.title()}"${resp ? ' (erro: ' + resp.message + ')' : ''}`)
    await aba.screenshot({ path: `${OUT}/tsi01-05c-fonte-oficial.png` })
    await aba.close()
  } else {
    note('TSI-01', 'nenhum link "Abrir no site oficial" na tela')
  }
  const verHistorico = page.getByRole('link', { name: 'Ver histórico' })
  if (await verHistorico.count()) await verHistorico.click()
  else await page.goto(`${BASE}/historico`)
  await page.waitForTimeout(1500)
  await shot(page, 'tsi01-06-historico')
  const hist = await page.locator('main').innerText()
  note('TSI-01', `histórico: ${hist.replace(/\s+/g, ' ').slice(0, 300)}`)
  await ctx.close()
}

// TSI-02: jornada de risco no check-in (P5 = Sim).
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  const email = `tsi02-${stamp}@exemplo.com`
  await cadastrarELogar(page, email, 'SenhaTeste123', 'tsi02')
  await fazerCheckin(page, ['Ruim', 'Bastante', 'Ruim', 'Bastante', 'Sim'], 'tsi02')
  const texto = await page.locator('main').innerText()
  note('TSI-02', `URL: ${page.url()}; CVV 188: ${texto.includes('188')}; SAMU 192: ${texto.includes('192')}`)
  await ctx.close()
}

// TSI-03: avaliação com resultado N1 (perfil B), respondida pela interface.
const OPCOES = ['Nenhuma vez', 'Vários dias', 'Mais da metade dos dias', 'Quase todos os dias']
async function responderAvaliacao(page, phq9, gad7) {
  const itens = page.locator('fieldset.avaliacao-item')
  const respostas = [...phq9, ...gad7]
  for (let k = 0; k < respostas.length; k++) {
    await itens.nth(k).getByLabel(OPCOES[respostas[k]], { exact: true }).check()
  }
}
let idAvaliacaoTsi03 = null
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  const email = `tsi03-${stamp}@exemplo.com`
  await cadastrarELogar(page, email, 'SenhaTeste123', 'tsi03')
  await page.getByRole('button', { name: 'Avaliação quinzenal' }).click()
  await page.waitForSelector('#avaliacao-title')
  const nItens = await page.locator('fieldset.avaliacao-item').count()
  const botaoAjuda = await page.getByRole('link', { name: /Preciso de ajuda agora/ }).isVisible()
  note('TSI-03', `tela da avaliação em ${page.url()}; ${nItens} itens; botão de ajuda visível: ${botaoAjuda}`)
  await shot(page, 'tsi03-04-avaliacao-vazia')
  await page.getByRole('button', { name: 'Concluir avaliação' }).click()
  await page.waitForTimeout(500)
  const alerta = await page.getByRole('alert').first().innerText().catch(() => '(sem alerta)')
  note('TSI-03', `envio sem respostas: URL ${page.url()}; alerta: ${alerta.replace(/\s+/g, ' ').slice(0, 120)}`)
  await responderAvaliacao(page, [2, 2, 1, 1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0, 0])
  await shot(page, 'tsi03-05-avaliacao-perfil-b')
  const respPost = page.waitForResponse((r) => r.url().endsWith('/api/avaliacoes') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Concluir avaliação' }).click()
  const post = await respPost
  note('TSI-03', `POST /api/avaliacoes → ${post.status()} ${JSON.stringify(await post.json()).slice(0, 200)}`)
  await page.waitForTimeout(1500)
  await shot(page, 'tsi03-06-resultado')
  const t = await page.locator('main').innerText()
  const links = await page.getByRole('link', { name: /site oficial/ }).count()
  note('TSI-03', `URL ${page.url()}; 10 de 27: ${t.includes('10 de 27')}; 5 de 21: ${t.includes('5 de 21')}; Moderada: ${/Faixa:\s*Moderada/.test(t)}; Leve: ${/Faixa:\s*Leve/.test(t)}; UBS: ${t.includes('UBS')}; "não é um diagnóstico": ${/não é um diagnóstico/i.test(t)}; materiais: ${links}`)
  await page.goto(`${BASE}/historico`)
  await page.waitForTimeout(1500)
  await shot(page, 'tsi03-07-historico')
  note('TSI-03', `histórico: ${(await page.locator('main').innerText()).replace(/\s+/g, ' ').slice(0, 400)}`)
  // Histórico sem check-in: o botão "Fazer o primeiro check-in" deve abrir o check-in (PR #78).
  const primeiro = page.getByRole('button', { name: 'Fazer o primeiro check-in' })
  if (await primeiro.count()) {
    await primeiro.click()
    await page.waitForTimeout(800)
    note('Histórico', `"Fazer o primeiro check-in" leva a ${page.url()}; título "${await page.locator('h1').first().innerText()}"`)
    await shot(page, 'historico-01-primeiro-checkin')
    await page.goto(`${BASE}/historico`)
    await page.waitForTimeout(1200)
  } else {
    note('Histórico', 'botão "Fazer o primeiro check-in" não encontrado')
  }
  const linkAval = page.locator('main a[href^="/avaliacoes/"]:not([href="/avaliacoes/nova"])').first()
  if (await linkAval.count()) {
    await linkAval.click()
    await page.waitForTimeout(1500)
    idAvaliacaoTsi03 = page.url().split('/').pop()
    await shot(page, 'tsi03-08-resultado-pelo-historico')
    const t2 = await page.locator('main').innerText()
    note('TSI-03', `resultado aberto pelo histórico: ${page.url()}; 10 de 27: ${t2.includes('10 de 27')}; materiais: ${await page.getByRole('link', { name: /site oficial/ }).count()}`)
  } else {
    note('TSI-03', 'nenhum link de avaliação no histórico')
  }
  await ctx.close()
}

// Verificação adicional (R10, perfil D): item 9 do PHQ-9 >= 1 abre a Tela de Ajuda, sem materiais.
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  await cadastrarELogar(page, `perfild-${stamp}@exemplo.com`, 'SenhaTeste123', 'perfild')
  await page.goto(`${BASE}/avaliacoes/nova`)
  await page.waitForSelector('#avaliacao-title')
  await responderAvaliacao(page, [0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0])
  const respPost = page.waitForResponse((r) => r.url().endsWith('/api/avaliacoes') && r.request().method() === 'POST')
  await page.getByRole('button', { name: 'Concluir avaliação' }).click()
  const post = await respPost
  await page.waitForTimeout(1200)
  const t = await page.locator('main').innerText()
  await shot(page, 'perfild-01-tela-ajuda')
  note('Perfil D', `POST → ${post.status()} ${JSON.stringify(await post.json())}; URL ${page.url()}; CVV 188: ${t.includes('188')}; SAMU 192: ${t.includes('192')}`)
  await ctx.close()
}

// TSI-05: exclusão de conta pela interface (Sprint 6, executado antes para o aceite da #61).
{
  const ctx = await browser.newContext()
  const page = await ctx.newPage()
  const email = `tsi05-${stamp}@exemplo.com`
  const senha = 'SenhaTeste123'
  await cadastrarELogar(page, email, senha, 'tsi05')
  await fazerCheckin(page, ['Ruim', 'Nada', 'Muito bom', 'Nada', 'Não'], 'tsi05')
  // Avaliação de outro usuário: deve aparecer como não encontrada (#58).
  if (idAvaliacaoTsi03) {
    await page.goto(`${BASE}/avaliacoes/${idAvaliacaoTsi03}`)
    await page.waitForTimeout(1200)
    await shot(page, 'tsi03-07-avaliacao-de-outro-usuario')
    note('TSI-03', `avaliação de outro usuário: ${(await page.locator('main').innerText()).replace(/\s+/g, ' ').slice(0, 200)}`)
  }
  await page.goto(`${BASE}/`)
  await page.waitForTimeout(800)
  await page.getByRole('button', { name: 'Excluir conta' }).click()
  await page.waitForTimeout(300)
  await shot(page, 'tsi05-06-confirmacao')
  note('TSI-05', `confirmação: ${(await page.getByRole('alertdialog').innerText()).replace(/\s+/g, ' ')}`)
  await page.getByRole('button', { name: 'Cancelar' }).click()
  await page.waitForTimeout(500)
  const aindaLogado = await page.evaluate(async () => {
    const token = sessionStorage.getItem('sintoniza.token')
    const r = await fetch('/api/me', { headers: { authorization: `Bearer ${token}` } })
    return r.status
  })
  note('TSI-05', `após Cancelar: GET /api/me → ${aindaLogado}; URL ${page.url()}`)
  await page.getByRole('button', { name: 'Excluir conta' }).click()
  const respDel = page.waitForResponse((r) => r.url().endsWith('/api/me') && r.request().method() === 'DELETE')
  await page.getByRole('button', { name: 'Excluir definitivamente' }).click()
  const del = await respDel
  await page.waitForTimeout(1500)
  await shot(page, 'tsi05-07-apos-excluir')
  const token = await page.evaluate(() => sessionStorage.getItem('sintoniza.token'))
  note('TSI-05', `DELETE /api/me → ${del.status()}; URL após excluir ${page.url()}; token na sessão: ${token === null ? 'removido' : 'presente'}`)
  await page.goto(`${BASE}/login`)
  await page.getByLabel('E-mail').fill(email)
  await page.getByLabel('Senha').fill(senha)
  const respLogin = page.waitForResponse((r) => r.url().endsWith('/api/auth/login'))
  await page.getByRole('button', { name: 'Entrar' }).click()
  const login = await respLogin
  await page.waitForTimeout(1000)
  await shot(page, 'tsi05-08-login-falha')
  note('TSI-05', `login com as mesmas credenciais → ${login.status()}; URL ${page.url()}; mensagem: ${(await page.locator('main').innerText()).replace(/\s+/g, ' ').slice(0, 160)}`)
  await ctx.close()
}

await browser.close()
fs.writeFileSync(`${OUT}/execucao.log`, log.join('\n') + '\n')
