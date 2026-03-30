import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import {
  MessageSquare,
  LayoutGrid,
  BookOpen,
  BarChart3,
  Settings,
} from "lucide-react";
import ChatPage from "./pages/ChatPage";
import CanvasPage from "./pages/CanvasPage";
import JournalPage from "./pages/JournalPage";
import OverviewPage from "./pages/OverviewPage";
import SettingsPage from "./pages/SettingsPage";

const navItems = [
  { to: "/overview", icon: BarChart3, label: "Overview" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/canvas", icon: LayoutGrid, label: "Canvas" },
  { to: "/journal", icon: BookOpen, label: "Journal" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export default function App() {
  return (
    <div className="flex h-screen">
      <nav className="flex w-16 flex-col items-center gap-1 border-r border-gray-800 bg-gray-900 py-4">
        <div className="mb-4 text-xl font-bold text-yoak-400">Y</div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            title={label}
            className={({ isActive }) =>
              `flex h-10 w-10 items-center justify-center rounded-lg transition ${
                isActive
                  ? "bg-yoak-600/20 text-yoak-400"
                  : "text-gray-500 hover:bg-gray-800 hover:text-gray-300"
              }`
            }
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
          <Route path="/journal" element={<JournalPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}
