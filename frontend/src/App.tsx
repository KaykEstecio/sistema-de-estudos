import { createBrowserRouter, createRoutesFromElements, Link, Navigate, Outlet, Route, RouterProvider, useLocation } from 'react-router'
import { ExitGuardProvider, useLogoutGuard } from './exitGuard'
import { AuthProvider, useAuth } from './auth'
import AuthPage from './pages/AuthPage'
import OnboardingPage from './pages/OnboardingPage'
import DiagnosticPage from './pages/DiagnosticPage'
import AssessmentPage from './pages/AssessmentPage'
import DashboardPage from './pages/DashboardPage'
import AttemptsPage, { AttemptDetailPage } from './pages/AttemptsPage'

function Shell() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const guarded = useLogoutGuard()
  function leave() {
    if (!guarded || window.confirm('Sair da conta? Alterações não salvas serão perdidas. Uma operação em andamento pode ter sido concluída no servidor.')) logout()
  }
  return <><a className="skip" href="#content">Pular para o conteúdo</a><header>
    <Link to="/" className="brand" aria-label="CodeTrack, início">Code<span>Track</span></Link>
    <nav aria-label="Principal">{user ? <><Link to="/dashboard">Meu painel</Link><Link to="/tentativas">Tentativas</Link><Link to="/onboarding">Meu perfil</Link><Link to="/diagnostico">Diagnóstico</Link><button onClick={leave} className="text-button">Sair</button></> : <Link to={location.pathname === '/cadastro' ? '/entrar' : '/cadastro'}>{location.pathname === '/cadastro' ? 'Entrar' : 'Criar conta'}</Link>}</nav>
  </header><div id="content"><Outlet /></div></>
}
function Protected() {
  const { user } = useAuth()
  const location = useLocation()
  return user ? <Outlet /> : <Navigate to="/entrar" replace state={{ from: location.pathname }} />
}
function Home() {
  const { user } = useAuth()
  return <Navigate replace to={user ? user.onboarding_completed ? '/dashboard' : '/onboarding' : '/entrar'} />
}
function DiagnosticEntry() {
  const { user } = useAuth()
  return user?.onboarding_completed ? <DiagnosticPage /> : <Navigate to="/onboarding" replace />
}
function AuthenticatedShell() {
  return <AuthProvider><ExitGuardProvider><Shell /></ExitGuardProvider></AuthProvider>
}
const router = createBrowserRouter(createRoutesFromElements(
  <Route element={<AuthenticatedShell />}>
    <Route index element={<Home />} />
    <Route path="entrar" element={<AuthPage key="login" />} />
    <Route path="cadastro" element={<AuthPage key="register" register />} />
    <Route element={<Protected />}>
      <Route path="dashboard" element={<DashboardEntry />} />
      <Route path="tentativas" element={<AttemptsEntry />} />
      <Route path="tentativas/:id" element={<AttemptDetailPage />} />
      <Route path="onboarding" element={<OnboardingPage />} />
      <Route path="diagnostico" element={<DiagnosticEntry />} />
      <Route path="diagnostico/:id" element={<AssessmentPage />} />
    </Route>
    <Route path="*" element={<main className="auth-main"><h1>Página não encontrada</h1><Link to="/">Voltar ao início</Link></main>} />
  </Route>,
))
export default function App() {
  return <RouterProvider router={router} />
}

function DashboardEntry() {
  const { user } = useAuth()
  return <DashboardPage key={user?.id} />
}

function AttemptsEntry() {
  const { user } = useAuth()
  return <AttemptsPage key={user?.id} />
}
