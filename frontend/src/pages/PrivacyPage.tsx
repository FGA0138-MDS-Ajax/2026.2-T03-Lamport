import { useEffect, useState } from 'react'
import { termsApi } from '../api/auth'

// Texto conforme o R03 (Visão, Quadro 14). Fontes: Visão, seções 1.1, 4.2, 4.5.1, 4.5.2, 4.5.5
// e requisitos R04, R05, R08, R12; Arquitetura, Figura 6 e seção 2.7.
// Ao mudar o texto, atualize TERMS_VERSION no backend.
export function PrivacyPage() {
  // The backend owns the version, since it is the one recorded when the terms are accepted.
  const [version, setVersion] = useState<string>()

  useEffect(() => {
    let active = true
    termsApi
      .get()
      .then((terms) => {
        if (active) setVersion(terms.version)
      })
      .catch(() => {})
    return () => {
      active = false
    }
  }, [])

  return (
    <article className="card prose" aria-labelledby="privacy-title">
      <h1 id="privacy-title">Termos de uso e privacidade</h1>
      {version && <p className="muted">Versão {version}</p>}

      <h2>O que é o Sintoniza</h2>
      <p>
        O Sintoniza é uma ferramenta de apoio e educação em saúde mental, para maiores de 18 anos.
        Ele não faz diagnóstico e não substitui psicólogo, psiquiatra ou serviço de urgência.
      </p>

      <h2>Quais dados guardamos e para quê</h2>

      <h3>Sua conta</h3>
      <ul>
        <li>
          <strong>E-mail:</strong> para identificar sua conta e permitir que você entre nela.
        </li>
        <li>
          <strong>Senha:</strong> para proteger o acesso à sua conta. A senha nunca é guardada como
          texto: guardamos apenas um código gerado a partir dela (hash Argon2id), que não permite
          descobrir a senha.
        </li>
        <li>
          <strong>Data de criação da conta:</strong> para registrar quando a sua conta foi criada.
        </li>
      </ul>

      <h3>Seu aceite destes termos</h3>
      <ul>
        <li>
          <strong>Versão dos termos que você aceitou e a data do aceite:</strong> para registrar que
          você concordou com o uso dos seus dados descrito aqui.
        </li>
      </ul>

      <h3>Respostas do check-in diário</h3>
      <ul>
        <li>
          <strong>O que guardamos:</strong> a data; suas respostas sobre humor, ansiedade, sono e
          sobrecarga, que são opcionais; sua resposta à pergunta sobre pensamentos de se machucar ou
          de que seria melhor estar morto(a), que é obrigatória; e o resultado calculado a partir
          delas (nível e temas dos conteúdos).
        </li>
        <li>
          <strong>Para quê:</strong> as respostas sobre humor, ansiedade, sono e sobrecarga servem
          apenas para escolher conteúdos de autocuidado e não são usadas para avaliar sua saúde. A
          resposta sobre pensamentos de se machucar serve apenas para mostrar a Tela de Ajuda
          Imediata quando você responde Sim. Seus check-ins também aparecem no seu histórico.
        </li>
      </ul>

      <h3>Respostas da avaliação quinzenal (PHQ-9 e GAD-7)</h3>
      <ul>
        <li>
          <strong>O que guardamos:</strong> suas respostas aos questionários PHQ-9 e GAD-7, a data,
          as pontuações, as faixas e o nível de orientação calculados a partir delas.
        </li>
        <li>
          <strong>Para quê:</strong> mostrar seu resultado com a orientação e os materiais
          indicados, mostrar a Tela de Ajuda Imediata quando as respostas indicarem risco e mostrar
          suas avaliações no seu histórico.
        </li>
      </ul>

      <h3>Conteúdos sugeridos a você</h3>
      <ul>
        <li>
          <strong>O que guardamos:</strong> quais materiais foram sugeridos a você, quando e por
          qual motivo.
        </li>
        <li>
          <strong>Para quê:</strong> explicar por que cada material foi sugerido e variar as
          sugestões, dando preferência aos materiais que você viu há mais tempo.
        </li>
      </ul>

      <h2>O que o Sintoniza não faz</h2>
      <ul>
        <li>
          <strong>Não faz diagnóstico.</strong> Os resultados do check-in e da avaliação são uma
          orientação, não um diagnóstico.
        </li>
        <li>
          <strong>Não monitora suas respostas.</strong> O Sintoniza não acompanha suas respostas em
          tempo real e não avisa ninguém: nem familiares, nem profissionais, nem serviços de
          emergência.
        </li>
      </ul>
      <p>
        Se você precisa de ajuda agora, use o botão “Preciso de ajuda agora” ou ligue para o CVV
        (188) ou para o SAMU (192).
      </p>

      <h2>Quem vê seus dados</h2>
      <p>Seus registros só aparecem para você, quando você entra na sua conta.</p>

      <h2>Como excluir sua conta</h2>
      <p>
        Você pode excluir sua conta a qualquer momento, quando estiver dentro dela. Depois que você
        confirmar, apagamos de forma definitiva a sua conta e todos os seus check-ins, avaliações e
        conteúdos sugeridos. Esses dados não podem ser recuperados depois.
      </p>

      <h2>Seus direitos</h2>
      <p>
        Informações sobre a sua saúde são dados pessoais sensíveis para a Lei Geral de Proteção de
        Dados Pessoais (Lei nº 13.709/2018). Só usamos esses dados porque você concordou com estes
        termos no cadastro, e você pode eliminá-los a qualquer momento excluindo a sua conta.
      </p>
    </article>
  )
}
