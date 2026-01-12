import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiFetch, setToken } from "../api.js";

export default function SocialCallback({ onLogin }) {
  const [message, setMessage] = useState("소셜 로그인 처리 중...");
  const navigate = useNavigate();

  useEffect(() => {
    let canceled = false;
    const exchange = async () => {
      try {
        const data = await apiFetch("/users/social/token/", {
          method: "GET",
          auth: false,
          credentials: "include",
        });
        if (canceled) return;
        setToken(data.token);
        if (onLogin) {
          onLogin(data.token);
        }
        setMessage(`환영합니다, ${data.user.name}!`);
        setTimeout(() => navigate("/"), 1000);
      } catch (error) {
        if (!canceled) {
          setMessage(`소셜 로그인 실패: ${error.message}`);
        }
      }
    };
    exchange();
    return () => {
      canceled = true;
    };
  }, [navigate, onLogin]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>소셜 로그인</h2>
          <p>구글 인증이 완료되면 자동으로 로그인됩니다.</p>
        </div>
        <span className="bubble">🪄 로그인 중</span>
      </header>
      <div className="card">
        <p>{message}</p>
      </div>
    </section>
  );
}
