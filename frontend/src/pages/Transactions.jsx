import { useEffect, useState } from "react";

import { apiFetch, cleanPayload } from "../api.js";

const initialForm = {
  account: "",
  amount: "",
  direction: "expense",
  method: "",
  description: "",
  occurred_at: "",
};

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [tags, setTags] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [categoryMode, setCategoryMode] = useState("select");
  const [customMethod, setCustomMethod] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);
  const [editingTx, setEditingTx] = useState(null);
  const [editForm, setEditForm] = useState(initialForm);
  const [editCategoryMode, setEditCategoryMode] = useState("select");
  const [editCustomMethod, setEditCustomMethod] = useState("");
  const [editTags, setEditTags] = useState([]);
  const [filters, setFilters] = useState({
    account: "",
    direction: "",
    min_amount: "",
    max_amount: "",
    start_date: "",
    end_date: "",
  });
  const [message, setMessage] = useState("");

  const fetchAccounts = async () => {
    try {
      const data = await apiFetch("/accounts/");
      setAccounts(data);
    } catch (error) {
      setMessage(`계좌 불러오기 실패: ${error.message}`);
    }
  };

  const fetchTransactions = async () => {
    try {
      const query = new URLSearchParams(cleanPayload(filters)).toString();
      const data = await apiFetch(`/transactions/${query ? `?${query}` : ""}`);
      setTransactions(data);
    } catch (error) {
      setMessage(`거래 불러오기 실패: ${error.message}`);
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await apiFetch("/categories/");
      setCategories(data);
    } catch (error) {
      setMessage(`카테고리 불러오기 실패: ${error.message}`);
    }
  };

  const fetchTags = async () => {
    try {
      const data = await apiFetch("/tags/");
      setTags(data);
    } catch (error) {
      setMessage(`태그 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchAccounts();
    fetchTransactions();
    fetchCategories();
    fetchTags();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      const method =
        categoryMode === "custom" ? customMethod.trim() : form.method;
      await apiFetch("/transactions/", {
        method: "POST",
        body: cleanPayload({
          ...form,
          amount: form.amount ? Number(form.amount) : form.amount,
          account: form.account ? Number(form.account) : form.account,
          method,
          tags: selectedTags,
        }),
      });
      setForm(initialForm);
      setCategoryMode("select");
      setCustomMethod("");
      setSelectedTags([]);
      fetchTransactions();
    } catch (error) {
      setMessage(`거래 등록 실패: ${error.message}`);
    }
  };

  const handleDelete = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/transactions/${id}/`, { method: "DELETE" });
      fetchTransactions();
    } catch (error) {
      setMessage(`거래 삭제 실패: ${error.message}`);
    }
  };

  const startEdit = (tx) => {
    setEditingTx(tx);
    setEditForm({
      account: String(tx.account),
      amount: String(tx.amount),
      direction: tx.direction,
      method: tx.method || "",
      description: tx.description || "",
      occurred_at: tx.occurred_at ? tx.occurred_at.slice(0, 16) : "",
    });
    const inCategories = categories.some((category) => category.name === tx.method);
    setEditCategoryMode(inCategories ? "select" : "custom");
    setEditCustomMethod(inCategories ? "" : tx.method || "");
    setEditTags((tx.tags || []).map((tag) => tag.id));
  };

  const cancelEdit = () => {
    setEditingTx(null);
    setEditForm(initialForm);
    setEditCategoryMode("select");
    setEditCustomMethod("");
    setEditTags([]);
  };

  const handleEditSubmit = async (event) => {
    event.preventDefault();
    if (!editingTx) return;
    setMessage("");
    try {
      const method =
        editCategoryMode === "custom" ? editCustomMethod.trim() : editForm.method;
      await apiFetch(`/transactions/${editingTx.id}/`, {
        method: "PATCH",
        body: cleanPayload({
          ...editForm,
          amount: editForm.amount ? Number(editForm.amount) : editForm.amount,
          account: editForm.account ? Number(editForm.account) : editForm.account,
          method,
          tags: editTags,
        }),
      });
      cancelEdit();
      fetchTransactions();
    } catch (error) {
      setMessage(`거래 수정 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>거래 내역</h2>
          <p>소비와 수입을 모두 기록해서 습관을 만들어요.</p>
        </div>
        <span className="bubble">🧾 꼼꼼 기록</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="card filters">
        <h3>필터</h3>
        <div className="filters-row">
          <select
            value={filters.account}
            onChange={(event) => setFilters({ ...filters, account: event.target.value })}
          >
            <option value="">전체 계좌</option>
            {accounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.name}
              </option>
            ))}
          </select>
          <select
            value={filters.direction}
            onChange={(event) => setFilters({ ...filters, direction: event.target.value })}
          >
            <option value="">전체 구분</option>
            <option value="income">수입</option>
            <option value="expense">지출</option>
            <option value="transfer">이체</option>
          </select>
          <input
            type="number"
            placeholder="최소 금액"
            value={filters.min_amount}
            onChange={(event) => setFilters({ ...filters, min_amount: event.target.value })}
          />
          <input
            type="number"
            placeholder="최대 금액"
            value={filters.max_amount}
            onChange={(event) => setFilters({ ...filters, max_amount: event.target.value })}
          />
          <input
            type="date"
            value={filters.start_date}
            onChange={(event) => setFilters({ ...filters, start_date: event.target.value })}
          />
          <input
            type="date"
            value={filters.end_date}
            onChange={(event) => setFilters({ ...filters, end_date: event.target.value })}
          />
          <button type="button" onClick={fetchTransactions}>
            적용하기
          </button>
        </div>
      </div>

      <div className="grid two">
        <div className="card">
          <h3>거래 목록</h3>
          <ul className="list">
            {transactions.map((tx) => (
              <li key={tx.id}>
                <div>
                  <strong>{tx.description || tx.method}</strong>
                  <span>{tx.account_name}</span>
                  {tx.tags?.length ? (
                    <span>{tx.tags.map((tag) => tag.name).join(", ")}</span>
                  ) : null}
                </div>
                <div className="list-meta">
                  <span className={`pill ${tx.direction}`}>{tx.direction}</span>
                  <span>{Number(tx.amount).toLocaleString()}원</span>
                  <button className="ghost" type="button" onClick={() => startEdit(tx)}>
                    수정
                  </button>
                  <button className="ghost" type="button" onClick={() => handleDelete(tx.id)}>
                    삭제
                  </button>
                </div>
              </li>
            ))}
            {!transactions.length && <li className="empty">거래가 아직 없어요.</li>}
          </ul>
        </div>

        <form className="card form" onSubmit={handleSubmit}>
          <h3>거래 등록</h3>
          <label>
            계좌
            <select
              value={form.account}
              onChange={(event) => setForm({ ...form, account: event.target.value })}
              required
            >
              <option value="">계좌 선택</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            금액
            <input
              type="number"
              value={form.amount}
              onChange={(event) => setForm({ ...form, amount: event.target.value })}
              required
            />
          </label>
          <label>
            구분
            <select
              value={form.direction}
              onChange={(event) => setForm({ ...form, direction: event.target.value })}
            >
              <option value="expense">지출</option>
              <option value="income">수입</option>
              <option value="transfer">이체</option>
            </select>
          </label>
          <label>
            카테고리/방법
            <select
              value={categoryMode === "custom" ? "__custom__" : form.method}
              onChange={(event) => {
                const value = event.target.value;
                if (value === "__custom__") {
                  setCategoryMode("custom");
                  setForm({ ...form, method: "" });
                } else {
                  setCategoryMode("select");
                  setForm({ ...form, method: value });
                }
              }}
              required={categoryMode !== "custom"}
            >
              <option value="">선택</option>
              {categories.map((category) => (
                <option key={category.id} value={category.name}>
                  {category.name}
                </option>
              ))}
              <option value="__custom__">직접 입력</option>
            </select>
          </label>
          {categoryMode === "custom" && (
            <label>
              직접 입력
              <input
                value={customMethod}
                onChange={(event) => setCustomMethod(event.target.value)}
                required
              />
            </label>
          )}
          <label>
            태그
            <select
              multiple
              value={selectedTags.map(String)}
              onChange={(event) => {
                const values = Array.from(event.target.selectedOptions).map((option) =>
                  Number(option.value)
                );
                setSelectedTags(values);
              }}
            >
              {tags.map((tag) => (
                <option key={tag.id} value={tag.id}>
                  {tag.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            설명
            <input
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </label>
          <label>
            발생일시
            <input
              type="datetime-local"
              value={form.occurred_at}
              onChange={(event) => setForm({ ...form, occurred_at: event.target.value })}
              required
            />
          </label>
          <button type="submit">등록하기</button>
        </form>
      </div>

      {editingTx && (
        <form className="card form" onSubmit={handleEditSubmit}>
          <div className="card-header">
            <h3>거래 수정</h3>
            <button type="button" className="ghost" onClick={cancelEdit}>
              닫기
            </button>
          </div>
          <label>
            계좌
            <select
              value={editForm.account}
              onChange={(event) => setEditForm({ ...editForm, account: event.target.value })}
              required
            >
              <option value="">계좌 선택</option>
              {accounts.map((account) => (
                <option key={account.id} value={account.id}>
                  {account.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            금액
            <input
              type="number"
              value={editForm.amount}
              onChange={(event) => setEditForm({ ...editForm, amount: event.target.value })}
              required
            />
          </label>
          <label>
            구분
            <select
              value={editForm.direction}
              onChange={(event) => setEditForm({ ...editForm, direction: event.target.value })}
            >
              <option value="expense">지출</option>
              <option value="income">수입</option>
              <option value="transfer">이체</option>
            </select>
          </label>
          <label>
            카테고리/방법
            <select
              value={editCategoryMode === "custom" ? "__custom__" : editForm.method}
              onChange={(event) => {
                const value = event.target.value;
                if (value === "__custom__") {
                  setEditCategoryMode("custom");
                  setEditForm({ ...editForm, method: "" });
                } else {
                  setEditCategoryMode("select");
                  setEditForm({ ...editForm, method: value });
                }
              }}
              required={editCategoryMode !== "custom"}
            >
              <option value="">선택</option>
              {categories.map((category) => (
                <option key={category.id} value={category.name}>
                  {category.name}
                </option>
              ))}
              <option value="__custom__">직접 입력</option>
            </select>
          </label>
          {editCategoryMode === "custom" && (
            <label>
              직접 입력
              <input
                value={editCustomMethod}
                onChange={(event) => setEditCustomMethod(event.target.value)}
                required
              />
            </label>
          )}
          <label>
            태그
            <select
              multiple
              value={editTags.map(String)}
              onChange={(event) => {
                const values = Array.from(event.target.selectedOptions).map((option) =>
                  Number(option.value)
                );
                setEditTags(values);
              }}
            >
              {tags.map((tag) => (
                <option key={tag.id} value={tag.id}>
                  {tag.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            설명
            <input
              value={editForm.description}
              onChange={(event) => setEditForm({ ...editForm, description: event.target.value })}
            />
          </label>
          <label>
            발생일시
            <input
              type="datetime-local"
              value={editForm.occurred_at}
              onChange={(event) => setEditForm({ ...editForm, occurred_at: event.target.value })}
              required
            />
          </label>
          <button type="submit">수정 저장</button>
        </form>
      )}
    </section>
  );
}
