import { useEffect, useState } from "react";

import { apiFetch, apiOrigin, buildQuery } from "../api.js";

export default function AnalysisPage() {
  const [analyses, setAnalyses] = useState([]);
  const [periodType, setPeriodType] = useState("");
  const [message, setMessage] = useState("");

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
