import { useEffect, useState } from "react";

import { apiFetch, clearToken } from "../api.js";

export default function ProfilePage({ onLogout }) {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({ name: "", phone: "" });
  const [refreshToken, setRefreshToken] = useState("");
  const [message, setMessage] = useState("");

  const fetchProfile = async () => {
    try {
      const data = await apiFetch("/users/profile/");
      setProfile(data);
      setForm({ name: data.name || "", phone: data.phone || "" });
    } catch (error) {
      setMessage(`프로필 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleUpdate = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      const data = await apiFetch("/users/profile/", {
        method: "PATCH",
        body: {
          name: form.name,
          phone: form.phone,
        },
      });
      setProfile(data);
      setMessage("프로필이 업데이트되었습니다.");
    } catch (error) {
      setMessage(`프로필 수정 실패: ${error.message}`);
    }
  };

  const handleLogout = async () => {
    setMessage("");
    try {
      if (refreshToken.trim()) {
        await apiFetch("/users/logout/", {
          method: "POST",
          body: { refresh: refreshToken.trim() },
        });
      }
    } catch (error) {
      setMessage(`서버 로그아웃 실패: ${error.message}`);
      return;
    }
    clearToken();
    if (onLogout) {
      onLogout(null);
    }
    setMessage("로그아웃되었습니다.");
  };

  const handleDelete = async () => {
    const confirmed = window.confirm("정말로 계정을 삭제할까요? 이 작업은 되돌릴 수 없습니다.");
    if (!confirmed) return;
    setMessage("");
    try {
      await apiFetch("/users/profile/", { method: "DELETE" });
      clearToken();
      if (onLogout) {
        onLogout(null);
      }
      setProfile(null);
      setMessage("계정이 삭제되었습니다.");
    } catch (error) {
      setMessage(`계정 삭제 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>내 프로필</h2>
          <p>이름/전화번호를 관리하고 로그아웃할 수 있어요.</p>
        </div>
        <span className="bubble">🧑‍💻 내 정보</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <div className="card">
          <h3>프로필 정보</h3>
          {profile ? (
            <ul className="list">
              <li>
                <div>
                  <strong>이메일</strong>
                  <span>{profile.email}</span>
                </div>
              </li>
              <li>
                <div>
                  <strong>이름</strong>
                  <span>{profile.name}</span>
                </div>
              </li>
              <li>
                <div>
                  <strong>전화번호</strong>
                  <span>{profile.phone || "미등록"}</span>
                </div>
              </li>
            </ul>
          ) : (
            <p className="muted">로그인이 필요합니다.</p>
          )}
          <button type="button" className="ghost" onClick={fetchProfile}>
            새로고침
          </button>
        </div>

        <form className="card form" onSubmit={handleUpdate}>
          <h3>프로필 수정</h3>
          <label>
            이름
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </label>
          <label>
            전화번호
            <input
              value={form.phone}
              onChange={(event) => setForm({ ...form, phone: event.target.value })}
            />
          </label>
          <button type="submit">수정하기</button>
        </form>
      </div>

      <div className="grid two">
        <div className="card form">
          <h3>로그아웃</h3>
          <p className="muted">
            리프레시 토큰이 필요한 경우 입력하세요. 비워도 로컬 토큰은 제거됩니다.
          </p>
          <label>
            리프레시 토큰 (선택)
            <input
              value={refreshToken}
              onChange={(event) => setRefreshToken(event.target.value)}
              placeholder="필요 시 입력"
            />
          </label>
          <button type="button" onClick={handleLogout}>
            로그아웃
          </button>
        </div>

        <div className="card">
          <h3>계정 삭제</h3>
          <p className="muted">모든 데이터가 삭제됩니다.</p>
          <button type="button" onClick={handleDelete}>
            계정 삭제
          </button>
        </div>
      </div>
    </section>
  );
}
