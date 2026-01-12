import { useState } from "react";

import { apiFetch, setToken } from "../api.js";

export default function AuthPage({ onLogin }) {
  const [signup, setSignup] = useState({
    email: "",
    password: "",
    name: "",
    phone: "",
  });
  const [login, setLogin] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");

  const handleSignup = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await apiFetch("/users/signup/", {
        method: "POST",
        body: {
          email: signup.email,
          password: signup.password,
          name: signup.name,
          phone: signup.phone,
        },
        auth: false,
      });
      setMessage("회원가입 완료! 이제 로그인해 주세요.");
      setSignup({ email: "", password: "", name: "", phone: "" });
    } catch (error) {
      setMessage(`회원가입 실패: ${error.message}`);
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      const data = await apiFetch("/users/login/", {
        method: "POST",
        body: login,
        auth: false,
      });
      setToken(data.token);
      if (onLogin) {
        onLogin(data.token);
      }
      setMessage(`환영합니다, ${data.user.name}!`);
      setLogin({ email: "", password: "" });
    } catch (error) {
      setMessage(`로그인 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>로그인 / 회원가입</h2>
          <p>토끼와 함께 쓰는 가계부, 시작해볼까요?</p>
        </div>
        <span className="bubble">🐣 환영해요</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <form className="card form" onSubmit={handleSignup}>
          <h3>회원가입</h3>
          <label>
            이메일
            <input
              type="email"
              value={signup.email}
              onChange={(event) => setSignup({ ...signup, email: event.target.value })}
              required
            />
          </label>
          <label>
            비밀번호
            <input
              type="password"
              value={signup.password}
              onChange={(event) => setSignup({ ...signup, password: event.target.value })}
              required
            />
          </label>
          <label>
            이름
            <input
              type="text"
              value={signup.name}
              onChange={(event) => setSignup({ ...signup, name: event.target.value })}
              required
            />
          </label>
          <label>
            전화번호
            <input
              type="text"
              value={signup.phone}
              onChange={(event) => setSignup({ ...signup, phone: event.target.value })}
            />
          </label>
          <button type="submit">가입하기</button>
        </form>

        <form className="card form" onSubmit={handleLogin}>
          <h3>로그인</h3>
          <label>
            이메일
            <input
              type="email"
              value={login.email}
              onChange={(event) => setLogin({ ...login, email: event.target.value })}
              required
            />
          </label>
          <label>
            비밀번호
            <input
              type="password"
              value={login.password}
              onChange={(event) => setLogin({ ...login, password: event.target.value })}
              required
            />
          </label>
          <button type="submit">로그인</button>
          <p className="hint">로그인 후 다른 페이지에서 토큰이 자동 적용돼요.</p>
        </form>
      </div>
    </section>
  );
}
