import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import {
  MessageSquare,
  LayoutGrid,
  BookOpen,
  BarChart3,
  Settings,
  ListChecks,
} from "lucide-react";
import ChatPage from "./pages/ChatPage";
import CanvasPage from "./pages/CanvasPage";
import HypothesesPage from "./pages/HypothesesPage";
import JournalPage from "./pages/JournalPage";
import OverviewPage from "./pages/OverviewPage";
import SettingsPage from "./pages/SettingsPage";
import { useTheme } from "./hooks/useTheme";

const navItems = [
  { to: "/overview", icon: BarChart3, label: "Overview" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/canvas", icon: LayoutGrid, label: "Canvas" },
  { to: "/hypotheses", icon: ListChecks, label: "Hypotheses" },
  { to: "/journal", icon: BookOpen, label: "Journal" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function App() {
  const { toggleTheme } = useTheme();

  return (
    <>
      <div className="shell-lines" aria-hidden="true" />
      <div className="brand-app flex h-screen">
        <nav className="brand-nav shrink-0">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            title="Toggle theme"
          >
            𓆉
          </button>
          <div className="mb-2 font-serif text-sm tracking-tight" style={{ color: "var(--moss)" }}>Yoak</div>
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              title={label}
              className={({ isActive }) => `brand-nav-link ${isActive ? "active" : ""}`}
            >
              <Icon size={20} />
            </NavLink>
          ))}
        </nav>

        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<OverviewPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/canvas" element={<CanvasPage />} />
            <Route path="/hypotheses" element={<HypothesesPage />} />
            <Route path="/journal" element={<JournalPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </>
  );
}
