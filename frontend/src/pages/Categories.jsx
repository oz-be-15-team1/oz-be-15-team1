import { useEffect, useState } from "react";

import { apiFetch, cleanPayload } from "../api.js";

const initialForm = {
  name: "",
  kind: "EXPENSE",
  sort_order: "0",
  parent: "",
};

export default function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [trash, setTrash] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const fetchCategories = async () => {
    try {
      const data = await apiFetch("/categories/");
      setCategories(data);
    } catch (error) {
      setMessage(`카테고리 불러오기 실패: ${error.message}`);
    }
  };

  const fetchTrash = async () => {
    try {
      const data = await apiFetch("/categories/trash/");
      setTrash(data);
    } catch (error) {
      setMessage(`휴지통 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await apiFetch("/categories/", {
        method: "POST",
        body: cleanPayload({
          ...form,
          sort_order: form.sort_order ? Number(form.sort_order) : undefined,
          parent: form.parent ? Number(form.parent) : undefined,
        }),
      });
      setForm(initialForm);
      fetchCategories();
    } catch (error) {
      setMessage(`카테고리 생성 실패: ${error.message}`);
    }
  };

  const handleDelete = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/categories/${id}/`, { method: "DELETE" });
      fetchCategories();
      fetchTrash();
    } catch (error) {
      setMessage(`카테고리 삭제 실패: ${error.message}`);
    }
  };

  const startEdit = (category) => {
    setEditingId(category.id);
    setEditForm({
      name: category.name || "",
      kind: category.kind || "EXPENSE",
      sort_order: String(category.sort_order ?? "0"),
      parent: category.parent ? String(category.parent) : "",
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm(initialForm);
  };

  const handleEdit = async (event) => {
    event.preventDefault();
    if (!editingId) return;
    setMessage("");
    try {
      await apiFetch(`/categories/${editingId}/`, {
        method: "PATCH",
        body: cleanPayload({
          ...editForm,
          sort_order: editForm.sort_order ? Number(editForm.sort_order) : undefined,
          parent: editForm.parent ? Number(editForm.parent) : undefined,
        }),
      });
      cancelEdit();
      fetchCategories();
    } catch (error) {
      setMessage(`카테고리 수정 실패: ${error.message}`);
    }
  };

  const handleRestore = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/categories/${id}/restore/`, { method: "POST" });
      fetchCategories();
      fetchTrash();
    } catch (error) {
      setMessage(`복구 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>카테고리</h2>
          <p>수입/지출 카테고리를 내 방식대로 꾸며요.</p>
        </div>
        <span className="bubble">🧸 분류 마법</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <div className="card">
          <h3>카테고리 목록</h3>
          <ul className="list">
            {categories.map((category) => (
              <li key={category.id}>
                <div>
                  <strong>{category.name}</strong>
                  <span>{category.kind}</span>
                </div>
                <div className="list-meta">
                  <span>정렬: {category.sort_order}</span>
                  <button type="button" className="ghost" onClick={() => startEdit(category)}>
                    수정
                  </button>
                  <button className="ghost" type="button" onClick={() => handleDelete(category.id)}>
                    삭제
                  </button>
                </div>
              </li>
            ))}
            {!categories.length && <li className="empty">카테고리를 추가해 주세요.</li>}
          </ul>
        </div>

        <form className="card form" onSubmit={handleSubmit}>
          <h3>카테고리 추가</h3>
          <label>
            이름
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </label>
          <label>
            종류
            <select
              value={form.kind}
              onChange={(event) => setForm({ ...form, kind: event.target.value })}
            >
              <option value="EXPENSE">지출</option>
              <option value="INCOME">수입</option>
            </select>
          </label>
          <label>
            정렬 순서
            <input
              type="number"
              value={form.sort_order}
              onChange={(event) => setForm({ ...form, sort_order: event.target.value })}
            />
          </label>
          <label>
            상위 카테고리 ID
            <input
              value={form.parent}
              onChange={(event) => setForm({ ...form, parent: event.target.value })}
              placeholder="선택 사항"
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
          {trash.map((category) => (
            <li key={category.id}>
              <div>
                <strong>{category.name}</strong>
                <span>{category.kind}</span>
              </div>
              <button type="button" onClick={() => handleRestore(category.id)}>
                복구
              </button>
            </li>
          ))}
          {!trash.length && <li className="empty">휴지통이 비어 있어요.</li>}
        </ul>
      </div>

      {editingId && (
        <form className="card form" onSubmit={handleEdit}>
          <div className="card-header">
            <h3>카테고리 수정</h3>
            <button type="button" className="ghost" onClick={cancelEdit}>
              닫기
            </button>
          </div>
          <label>
            이름
            <input
              value={editForm.name}
              onChange={(event) => setEditForm({ ...editForm, name: event.target.value })}
              required
            />
          </label>
          <label>
            종류
            <select
              value={editForm.kind}
              onChange={(event) => setEditForm({ ...editForm, kind: event.target.value })}
            >
              <option value="EXPENSE">지출</option>
              <option value="INCOME">수입</option>
            </select>
          </label>
          <label>
            정렬 순서
            <input
              type="number"
              value={editForm.sort_order}
              onChange={(event) => setEditForm({ ...editForm, sort_order: event.target.value })}
            />
          </label>
          <label>
            상위 카테고리 ID
            <input
              value={editForm.parent}
              onChange={(event) => setEditForm({ ...editForm, parent: event.target.value })}
              placeholder="선택 사항"
            />
          </label>
          <button type="submit">수정 저장</button>
        </form>
      )}
    </section>
  );
}
