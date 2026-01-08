import { useState } from "react";
import { NavLink, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard.jsx";
import AuthPage from "./pages/Auth.jsx";
import AccountsPage from "./pages/Accounts.jsx";
import TransactionsPage from "./pages/Transactions.jsx";
import CategoriesPage from "./pages/Categories.jsx";
import TagsPage from "./pages/Tags.jsx";
import AnalysisPage from "./pages/Analysis.jsx";
import NotificationsPage from "./pages/Notifications.jsx";
import { apiOrigin, clearToken, getToken } from "./api.js";

const navItems = [
  { to: "/", label: "대시보드" },
  { to: "/auth", label: "로그인/회원가입" },
  { to: "/accounts", label: "계좌" },
  { to: "/transactions", label: "거래" },
  { to: "/categories", label: "카테고리" },
  { to: "/tags", label: "태그" },
  { to: "/analysis", label: "분석" },
  { to: "/notifications", label: "알림" },
];

export default function App() {
  const [token, setTokenState] = useState(getToken());

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-badge">🐰</span>
          <div>
            <h1>Budget Buddy</h1>
            <p>귀엽고 똑똑한 가계부</p>
          </div>
        </div>
        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="token-card">
          <p>{token ? "로그인 됨" : "로그인 필요"}</p>
          {token && (
            <button
              type="button"
              className="ghost"
              onClick={() => {
                clearToken();
                setTokenState(null);
              }}
            >
              로그아웃
            </button>
          )}
          <a
            className="docs"
            href={apiOrigin ? `${apiOrigin}/api/docs/` : "/api/docs/"}
            target="_blank"
            rel="noreferrer"
          >
            API 문서 보기
          </a>
        </div>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/auth" element={<AuthPage onLogin={setTokenState} />} />
          <Route path="/accounts" element={<AccountsPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/tags" element={<TagsPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
        </Routes>
      </main>
    </div>
  );
}
