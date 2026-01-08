import { useEffect, useState } from "react";

import { apiFetch, cleanPayload } from "../api.js";

const initialForm = {
  name: "",
  color: "",
};

export default function TagsPage() {
  const [tags, setTags] = useState([]);
  const [trash, setTrash] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const fetchTags = async () => {
    try {
      const data = await apiFetch("/tags/");
      setTags(data);
    } catch (error) {
      setMessage(`태그 불러오기 실패: ${error.message}`);
    }
  };

  const fetchTrash = async () => {
    try {
      const data = await apiFetch("/tags/trash/");
      setTrash(data);
    } catch (error) {
      setMessage(`휴지통 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await apiFetch("/tags/", {
        method: "POST",
        body: cleanPayload(form),
      });
      setForm(initialForm);
      fetchTags();
    } catch (error) {
      setMessage(`태그 생성 실패: ${error.message}`);
    }
  };

  const handleDelete = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/tags/${id}/`, { method: "DELETE" });
      fetchTags();
      fetchTrash();
    } catch (error) {
      setMessage(`태그 삭제 실패: ${error.message}`);
    }
  };

  const handleRestore = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/tags/${id}/restore/`, { method: "POST" });
      fetchTags();
      fetchTrash();
    } catch (error) {
      setMessage(`복구 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>태그</h2>
          <p>귀여운 색상으로 나만의 태그를 만들어요.</p>
        </div>
        <span className="bubble">🎀 색상 모음</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <div className="card">
          <h3>태그 목록</h3>
          <ul className="list">
            {tags.map((tag) => (
              <li key={tag.id}>
                <div>
                  <strong>{tag.name}</strong>
                  <span className="tag" style={{ backgroundColor: tag.color || "#ffd6e0" }}>
                    {tag.color || "기본"}
                  </span>
                </div>
                <button className="ghost" type="button" onClick={() => handleDelete(tag.id)}>
                  삭제
                </button>
              </li>
            ))}
            {!tags.length && <li className="empty">태그를 만들어 볼까요?</li>}
          </ul>
        </div>

        <form className="card form" onSubmit={handleSubmit}>
          <h3>태그 추가</h3>
          <label>
            이름
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </label>
          <label>
            컬러
            <input
              value={form.color}
              onChange={(event) => setForm({ ...form, color: event.target.value })}
              placeholder="#ffb3c7"
            />
          </label>
          <button type="submit">추가하기</button>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>휴지통</h3>
          <button type="button" onClick={fetchTrash}>
            새로고침
          </button>
        </div>
        <ul className="list">
          {trash.map((tag) => (
            <li key={tag.id}>
              <div>
                <strong>{tag.name}</strong>
                <span className="tag" style={{ backgroundColor: tag.color || "#ffd6e0" }}>
                  {tag.color || "기본"}
                </span>
              </div>
              <button type="button" onClick={() => handleRestore(tag.id)}>
                복구
              </button>
            </li>
          ))}
          {!trash.length && <li className="empty">휴지통이 비어 있어요.</li>}
        </ul>
      </div>
    </section>
  );
}
