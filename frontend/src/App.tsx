import { createBrowserRouter, createRoutesFromElements, Link, NavLink, Navigate, Outlet, Route, RouterProvider, useLocation } from 'react-router'
import { ExitGuardProvider, useLogoutGuard } from './exitGuard'
import { AuthProvider, useAuth } from './auth'
import ThemeSelect from './ThemeSelect'
import StudyPage, { StudyDetailPage, CreateStudyPage } from './pages/StudyPage'
import AdminReviewsPage, { AdminReviewPage } from './pages/AdminReviewsPage'
import LearningIcon from './LearningIcon'
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
  return <><a className="skip" href="#content">Pular para o conteúdo</a><header className="site-header">
    <Link to="/" className="brand" aria-label="CodeTrack, início"><span className="brand-mark" aria-hidden="true">/c</span>Code<span>Track</span></Link>
    <nav aria-label="Principal">{user ? <><NavLink to="/dashboard"><LearningIcon name="home" />Meu painel</NavLink><NavLink to="/estudar">Estudar</NavLink><NavLink to="/tentativas"><LearningIcon name="code" />Tentativas</NavLink><NavLink to="/onboarding"><LearningIcon name="profile" />Meu perfil</NavLink><NavLink to="/diagnostico"><LearningIcon name="target" />Diagnóstico</NavLink>{user.role === 'ADMIN' && <NavLink to="/admin/revisoes"><LearningIcon name="review" />Revisar</NavLink>}<button onClick={leave} className="text-button logout-button">Sair</button></> : <Link className="header-action" to={location.pathname === '/cadastro' ? '/entrar' : '/cadastro'}>{location.pathname === '/cadastro' ? 'Entrar' : 'Criar conta'}</Link>}</nav>
    <ThemeSelect />
  </header><div id="content" tabIndex={-1}><Outlet /></div></>
}
function Protected() {
  const { user } = useAuth()
  const location = useLocation()
  return user ? <Outlet /> : <Navigate to="/entrar" replace state={{ from: location.pathname }} />
}
function AdminOnly() {
  const { user } = useAuth()
  return user?.role === 'ADMIN' ? <Outlet /> : <main className="auth-main"><h1>Acesso restrito</h1><p>Esta área exige uma conta ADMIN.</p><Link to="/">Voltar ao início</Link></main>
}
function AdminReviewEntry() {
  const { user } = useAuth()
  const { pathname } = useLocation()
  return <AdminReviewPage key={`${user?.id}:${pathname}`} />
}
function StudyEntry({ detail = false }: { detail?: boolean }) {
  const { user } = useAuth()
  const location = useLocation()
  return detail ? <StudyDetailPage key={`${user?.id}:${location.pathname}`} /> : <StudyPage key={`${user?.id}:${location.search}`} />
}
function Home() {
  const { user } = useAuth()
  return <Navigate replace to={user ? user.role === 'ADMIN' ? '/admin/revisoes' : user.onboarding_completed ? '/dashboard' : '/onboarding' : '/entrar'} />
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
      <Route element={<AdminOnly />}>
        <Route path="admin/conteudos/novo" element={<CreateStudyPage />} />
        <Route path="admin/revisoes" element={<AdminReviewsPage />} />
        <Route path="admin/revisoes/:id" element={<AdminReviewEntry />} />
      </Route>
      <Route path="dashboard" element={<DashboardEntry />} />
      <Route path="estudar" element={<StudyEntry />} />
      <Route path="estudar/:id" element={<StudyEntry detail />} />
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
