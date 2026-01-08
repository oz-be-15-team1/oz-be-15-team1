import { useEffect, useState } from "react";

import { apiFetch, apiOrigin, buildQuery } from "../api.js";

export default function AnalysisPage() {
  const [analyses, setAnalyses] = useState([]);
  const [periodType, setPeriodType] = useState("");
  const [message, setMessage] = useState("");
  const [taskId, setTaskId] = useState("");
  const [taskStatus, setTaskStatus] = useState("");
  const [runForm, setRunForm] = useState({
    about: "total_expense",
    type: "weekly",
    period_start: "",
    period_end: "",
  });

  const fetchAnalyses = async () => {
    try {
      const path = periodType
        ? `/analyses/period/${buildQuery({ type: periodType })}`
        : "/analyses/";
      const data = await apiFetch(path);
      setAnalyses(data);
    } catch (error) {
      setMessage(`분석 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchAnalyses();
  }, [periodType]);

  useEffect(() => {
    if (!taskId) return;
    let canceled = false;
    let timer;
    const poll = async () => {
      try {
        const data = await apiFetch(`/analyses/tasks/${taskId}/`);
        if (canceled) return;
        setTaskStatus(data.status);
        if (data.status === "SUCCESS") {
          fetchAnalyses();
          if (timer) {
            clearInterval(timer);
          }
        }
      } catch (error) {
        if (!canceled) {
          setTaskStatus("ERROR");
        }
      }
    };
    poll();
    timer = setInterval(poll, 3000);
    return () => {
      canceled = true;
      clearInterval(timer);
    };
  }, [taskId]);

  const resolveImage = (value) => {
    if (!value) return "";
    if (value.startsWith("http")) return value;
    return `${apiOrigin}${value.startsWith("/") ? value : `/${value}`}`;
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>분석 리포트</h2>
          <p>주간/월간 분석 결과를 모아볼 수 있어요.</p>
        </div>
        <span className="bubble">📊 분석 요정</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <form
        className="card form"
        onSubmit={async (event) => {
          event.preventDefault();
          setMessage("");
          try {
            const data = await apiFetch("/analyses/run/", {
              method: "POST",
              body: runForm,
            });
            setTaskId(data.task_id);
            setTaskStatus("PENDING");
            setMessage(`분석 요청 완료! 작업 ID: ${data.task_id}`);
          } catch (error) {
            setMessage(`분석 요청 실패: ${error.message}`);
          }
        }}
      >
        <h3>분석 요청</h3>
        <label>
          분석 종류
          <select
            value={runForm.about}
            onChange={(event) => setRunForm({ ...runForm, about: event.target.value })}
          >
            <option value="total_expense">총 지출</option>
            <option value="total_income">총 수입</option>
            <option value="category_expense">카테고리별 지출</option>
            <option value="account_balance">계좌 잔액</option>
          </select>
        </label>
        <label>
          기간 유형
          <select
            value={runForm.type}
            onChange={(event) => setRunForm({ ...runForm, type: event.target.value })}
          >
            <option value="weekly">주간</option>
            <option value="monthly">월간</option>
          </select>
        </label>
        <label>
          시작일
          <input
            type="date"
            value={runForm.period_start}
            onChange={(event) => setRunForm({ ...runForm, period_start: event.target.value })}
            required
          />
        </label>
        <label>
          종료일
          <input
            type="date"
            value={runForm.period_end}
            onChange={(event) => setRunForm({ ...runForm, period_end: event.target.value })}
            required
          />
        </label>
        <button type="submit">분석 요청</button>
        {taskId && (
          <div className="hint">
            작업 상태: {taskStatus || "확인 중..."} · ID: {taskId}
          </div>
        )}
      </form>

      <div className="card filters">
        <h3>기간 필터</h3>
        <div className="filters-row">
          <select value={periodType} onChange={(event) => setPeriodType(event.target.value)}>
            <option value="">전체</option>
            <option value="weekly">주간</option>
            <option value="monthly">월간</option>
          </select>
          <button type="button" onClick={fetchAnalyses}>
            새로고침
          </button>
        </div>
      </div>

      <div className="grid">
        {analyses.map((analysis) => (
          <article key={analysis.id} className="card analysis-card">
            <div>
              <h3>{analysis.about}</h3>
              <p className="muted">
                {analysis.type} · {analysis.period_start} ~ {analysis.period_end}
              </p>
              <p>{analysis.description}</p>
            </div>
            {analysis.result_image && (
              <img src={resolveImage(analysis.result_image)} alt="분석 그래프" />
            )}
          </article>
        ))}
        {!analyses.length && <div className="empty">아직 분석 결과가 없어요.</div>}
      </div>
    </section>
  );
}
