import { Route, Routes } from 'react-router'
import { GuestOnly, RequireAuth } from './auth/RouteGuards'
import { Layout } from './components/Layout'
import { HomePage } from './pages/HomePage'
import { LoginPage } from './pages/LoginPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { PrivacyPage } from './pages/PrivacyPage'
import { RegisterPage } from './pages/RegisterPage'
import { DailyCheckin } from './pages/DailyCheckin'
import { AjudaPage } from './pages/AjudaPage'
import { HistoryPage } from './pages/HistoryPage'
import { AJUDA_PATH } from './constants/ajuda'

export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route element={<RequireAuth />}>
          <Route index element={<HomePage />} />
          <Route path="dailycheckin" element={<DailyCheckin />} />
          <Route path="historico" element={<HistoryPage />} />
        </Route>
        <Route element={<GuestOnly />}>
          <Route path="login" element={<LoginPage />} />
          <Route path="cadastro" element={<RegisterPage />} />
        </Route>
        <Route path="privacidade" element={<PrivacyPage />} />
        {/* Pública: fora de RequireAuth e de GuestOnly (R11; Arquitetura, seção 2.4, item 3). */}
        <Route path={AJUDA_PATH} element={<AjudaPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
