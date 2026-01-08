import { Link } from "react-router-dom";

const cards = [
  {
    title: "오늘의 소비",
    body: "거래 내역을 입력하고 습관을 확인해요!",
    to: "/transactions",
  },
  {
    title: "내 계좌",
    body: "은행/카드/현금 계좌를 한 번에 관리해요.",
    to: "/accounts",
  },
  {
    title: "분석 리포트",
    body: "주간/월간 그래프로 소비 패턴을 봐요.",
    to: "/analysis",
  },
  {
    title: "알림함",
    body: "완료된 분석 소식을 한눈에 확인해요.",
    to: "/notifications",
  },
];

export default function Dashboard() {
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>대시보드</h2>
          <p>오늘도 귀엽고 꼼꼼하게 기록해요!</p>
        </div>
        <span className="bubble">✨ 반짝반짝</span>
      </header>

      <div className="grid">
        {cards.map((card) => (
          <Link key={card.title} to={card.to} className="card">
            <h3>{card.title}</h3>
            <p>{card.body}</p>
            <span className="card-cta">바로가기 →</span>
          </Link>
        ))}
      </div>

      <div className="wide-card">
        <div>
          <h3>오늘의 미션</h3>
          <p>거래 1건 이상 기록하면 토끼 스티커를 받을 수 있어요.</p>
        </div>
        <span className="sticker">🐾</span>
      </div>
    </section>
  );
}
