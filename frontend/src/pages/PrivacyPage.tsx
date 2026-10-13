// Must match TERMS_VERSION on the backend, which records the accepted version.
const TERMS_VERSION = '2026-10'

export function PrivacyPage() {
  return (
    <article className="card prose" aria-labelledby="privacy-title">
      <h1 id="privacy-title">Termos de uso e privacidade</h1>
      <p className="muted">Versão {TERMS_VERSION}</p>

      <h2>O que é o Sintoniza</h2>
      <p>
        O Sintoniza é uma ferramenta de apoio e orientação inicial em saúde mental. Ele não realiza
        diagnósticos e não substitui o acompanhamento de psicólogos, psiquiatras ou serviços de
        urgência. Em situação de emergência, procure ajuda imediata: SAMU (192) ou CVV (188).
      </p>

      <h2>Quais dados coletamos</h2>
      <ul>
        <li>Seu e-mail, usado para identificar sua conta.</li>
        <li>
          Sua senha, armazenada apenas de forma cifrada por um algoritmo irreversível. Nem a equipe
          do Sintoniza tem acesso a ela.
        </li>
        <li>A data de criação da conta e o registro do seu aceite a estes termos.</li>
      </ul>
      <p>
        Novas categorias de dados só serão coletadas depois de você ser informado e, quando
        aplicável, de concordar com elas.
      </p>

      <h2>Como usamos seus dados</h2>
      <p>
        Os dados são usados exclusivamente para permitir o acesso à sua conta. Eles não são vendidos
        nem compartilhados com terceiros, e o acesso é restrito a você.
      </p>

      <h2>Seus direitos</h2>
      <p>
        Conforme a Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018), você pode solicitar
        acesso, correção e exclusão dos seus dados pessoais.
      </p>
    </article>
  )
}
