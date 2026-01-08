import { useEffect, useState } from "react";

import { apiFetch } from "../api.js";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [unread, setUnread] = useState([]);
  const [message, setMessage] = useState("");

  const fetchAll = async () => {
    try {
      const data = await apiFetch("/notifications/");
      setNotifications(data);
    } catch (error) {
      setMessage(`알림 불러오기 실패: ${error.message}`);
    }
  };

  const fetchUnread = async () => {
    try {
      const data = await apiFetch("/notifications/unread/");
      setUnread(data);
    } catch (error) {
      setMessage(`미확인 알림 불러오기 실패: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchAll();
    fetchUnread();
  }, []);

  const handleMarkRead = async (id) => {
    setMessage("");
    try {
      await apiFetch(`/notifications/${id}/read/`, { method: "PATCH" });
      fetchAll();
      fetchUnread();
    } catch (error) {
      setMessage(`읽음 처리 실패: ${error.message}`);
    }
  };

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h2>알림함</h2>
          <p>새로운 분석 소식을 놓치지 마세요.</p>
        </div>
        <span className="bubble">🔔 띵동</span>
      </header>

      {message && <div className="notice">{message}</div>}

      <div className="grid two">
        <div className="card">
          <div className="card-header">
            <h3>미확인 알림</h3>
            <button type="button" onClick={fetchUnread}>
              새로고침
            </button>
          </div>
          <ul className="list">
            {unread.map((item) => (
              <li key={item.id}>
                <div>
                  <strong>{item.message}</strong>
                  <span>{item.created_at}</span>
                </div>
                <button type="button" onClick={() => handleMarkRead(item.id)}>
                  읽음
                </button>
              </li>
            ))}
            {!unread.length && <li className="empty">미확인 알림이 없어요.</li>}
          </ul>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>전체 알림</h3>
            <button type="button" onClick={fetchAll}>
              새로고침
            </button>
          </div>
          <ul className="list">
            {notifications.map((item) => (
              <li key={item.id}>
                <div>
                  <strong>{item.message}</strong>
                  <span>{item.created_at}</span>
                </div>
                {!item.is_read && (
                  <button type="button" onClick={() => handleMarkRead(item.id)}>
                    읽음
                  </button>
                )}
              </li>
            ))}
            {!notifications.length && <li className="empty">알림이 아직 없어요.</li>}
          </ul>
        </div>
      </div>
    </section>
  );
}
