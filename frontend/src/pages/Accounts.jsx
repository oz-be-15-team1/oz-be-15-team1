import { useEffect, useState } from "react";

import { apiFetch, cleanPayload } from "../api.js";

const initialForm = {
  name: "",
  source_type: "bank",
  balance: "",
  account_number: "",
  bank_code: "",
  account_type: "",
  card_company: "",
  card_number: "",
  billing_day: "",
};

export default function AccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [message, setMessage] = useState("");

  const fetchAccounts = async () => {
    try {
      const data = await apiFetch("/accounts/");
      setAccounts(data);
    } catch (error) {
      setMessage(`계좌 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    try {
      await apiFetch("/accounts/", {
        method: "POST",
        body: cleanPayload({
          ...form,
          balance: form.balance ? Number(form.balance) : form.balance,
          billing_day: form.billing_day ? Number(form.billing_day) : form.billing_day,
        }),
      });
      setForm(initialForm);
      fetchAccounts();
    } catch (error) {
      setMessage(`계좌 생성 실패: ${error.message}`);
    }
  };

  const handleDelete = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/accounts/${id}/`, { method: "DELETE" });
      fetchAccounts();
    } catch (error) {
      setMessage(`계좌 삭제 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>계좌 관리</h2>
          <p>은행/카드/현금 계좌를 깔끔하게 정리해요.</p>
        </div>
        <span className="bubble">💳 반짝 계좌</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <div className="card">
          <h3>계좌 목록</h3>
          <ul className="list">
            {accounts.map((account) => (
              <li key={account.id}>
                <div>
                  <strong>{account.name}</strong>
                  <span>{account.source_type}</span>
                </div>
                <div className="list-meta">
                  <span>{Number(account.balance).toLocaleString()}원</span>
                  <button className="ghost" type="button" onClick={() => handleDelete(account.id)}>
                    삭제
                  </button>
                </div>
              </li>
            ))}
            {!accounts.length && <li className="empty">아직 계좌가 없어요.</li>}
          </ul>
        </div>

        <form className="card form" onSubmit={handleSubmit}>
          <h3>새 계좌 만들기</h3>
          <label>
            계좌 이름
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
          </label>
          <label>
            구분
            <select
              value={form.source_type}
              onChange={(event) => setForm({ ...form, source_type: event.target.value })}
            >
              <option value="bank">은행</option>
              <option value="card">카드</option>
              <option value="cash">현금</option>
            </select>
          </label>
          <label>
            잔액
            <input
              type="number"
              value={form.balance}
              onChange={(event) => setForm({ ...form, balance: event.target.value })}
              required
            />
          </label>
          <label>
            계좌 번호
            <input
              value={form.account_number}
              onChange={(event) => setForm({ ...form, account_number: event.target.value })}
            />
          </label>
          <label>
            은행 코드
            <input
              value={form.bank_code}
              onChange={(event) => setForm({ ...form, bank_code: event.target.value })}
            />
          </label>
          <label>
            카드사
            <input
              value={form.card_company}
              onChange={(event) => setForm({ ...form, card_company: event.target.value })}
            />
          </label>
          <label>
            결제일
            <input
              type="number"
              value={form.billing_day}
              onChange={(event) => setForm({ ...form, billing_day: event.target.value })}
            />
          </label>
          <button type="submit">저장하기</button>
        </form>
      </div>
    </section>
  );
}
