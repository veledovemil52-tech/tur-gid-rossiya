import "./App.css";

const BOT_URL = "https://max.ru/se14052982_bot";

const features = [
  {
    number: "01",
    icon: "✦",
    title: "AI-маршрут",
    text: "Персональный план поездки с учётом интересов, компании и темпа путешествия.",
  },
  {
    number: "02",
    icon: "☼",
    title: "Погода",
    text: "Маршрут адаптируется под прогноз, чтобы дождь или жара не испортили день.",
  },
  {
    number: "03",
    icon: "₽",
    title: "Бюджет",
    text: "ТурГид учитывает бюджет и помогает собрать поездку без лишних расходов.",
  },
  {
    number: "04",
    icon: "↗",
    title: "Маршрут на карте",
    text: "Готовый маршрут можно открыть на карте и сразу отправиться в путь.",
  },
];

const destinations = [
  ["Санкт-Петербург", "Эрмитаж · Невский · набережные"],
  ["Казань", "Кремль · Старо-Татарская слобода"],
  ["Сочи", "море · горы · прогулки"],
  ["Москва", "Красная площадь · парки · музеи"],
];

function App() {
  const openBot = () => {
    window.open(BOT_URL, "_blank", "noopener,noreferrer");
  };

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="site">
      <header className="header">
        <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
          <span className="brand-mark">T</span>
          <span>ТурГид <strong>Россия</strong></span>
        </button>

        <nav>
          <button onClick={() => scrollTo("how")}>Как это работает</button>
          <button onClick={() => scrollTo("features")}>Возможности</button>
          <button onClick={() => scrollTo("destinations")}>Направления</button>
          <button onClick={openBot}>MAX ↗</button>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-glow glow-blue" />
          <div className="hero-glow glow-gold" />

          <div className="hero-copy">
            <div className="eyebrow">
              <span className="dot" />
              Умный AI-гид по России
            </div>

            <h1>
              Путешествия
              <span>начинаются</span>
              <b>здесь.</b>
            </h1>

            <p className="hero-text">
              ТурГид Россия создаёт персональный маршрут по России —
              с учётом твоих интересов, бюджета, компании и погоды.
            </p>

            <div className="hero-actions">
              <button className="primary-btn" onClick={openBot}>
                Запустить в MAX <span>→</span>
              </button>
              <button className="secondary-btn" onClick={() => scrollTo("how")}>
                Как это работает
              </button>
            </div>

            <div className="stats">
              <div>
                <strong>89+</strong>
                <span>городов России</span>
              </div>
              <div>
                <strong>AI</strong>
                <span>персональный маршрут</span>
              </div>
              <div>
                <strong>24/7</strong>
                <span>помощник в поездке</span>
              </div>
            </div>
          </div>

          <div className="hero-visual">
            <div className="route-card">
              <div className="route-top">
                <span>ТВОЙ МАРШРУТ</span>
                <span className="days-pill">5 дней</span>
              </div>

              <div className="route-line">
                <span className="route-point active" />
                <div>
                  <small>01 · 10:00</small>
                  <strong>Эрмитаж</strong>
                  <span>Дворцовая площадь</span>
                </div>
              </div>

              <div className="route-line">
                <span className="route-point" />
                <div>
                  <small>02 · 14:30</small>
                  <strong>Невский проспект</strong>
                  <span>Прогулка по центру</span>
                </div>
              </div>

              <div className="route-line">
                <span className="route-point" />
                <div>
                  <small>03 · 19:20</small>
                  <strong>Финский залив</strong>
                  <span>Закат и отдых</span>
                </div>
              </div>

              <div className="route-bottom">
                <span>Бюджет поездки</span>
                <strong>24 500 ₽</strong>
              </div>
            </div>

            <div className="floating-ai">
              <span>✦</span>
              <div>
                <small>ТурГид AI</small>
                <strong>Маршрут готов</strong>
              </div>
            </div>

            <div className="floating-weather">
              <span>☼</span>
              <div>
                <strong>+21°</strong>
                <small>идеально для прогулки</small>
              </div>
            </div>
          </div>
        </section>

        <section className="intro-strip">
          <span>Планируй меньше.</span>
          <strong>Путешествуй больше.</strong>
          <span>Остальное сделает ТурГид.</span>
        </section>

        <section className="section how" id="how">
          <div className="section-heading">
            <div>
              <span className="section-kicker">01 / ПРОСТОЙ СЦЕНАРИЙ</span>
              <h2>От идеи до маршрута<br /><em>за несколько шагов.</em></h2>
            </div>
            <p>Не нужно часами собирать информацию. ТурГид превращает твои пожелания в готовый план путешествия.</p>
          </div>

          <div className="steps">
            <article>
              <span>01</span>
              <h3>Выбери город</h3>
              <p>Москва, Казань, Сочи или любой другой город России.</p>
            </article>
            <article>
              <span>02</span>
              <h3>Расскажи о себе</h3>
              <p>Интересы, компания, количество дней и бюджет поездки.</p>
            </article>
            <article>
              <span>03</span>
              <h3>Получи маршрут</h3>
              <p>AI соберёт программу дня и адаптирует её под погоду.</p>
            </article>
          </div>
        </section>

        <section className="section features" id="features">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">02 / ВОЗМОЖНОСТИ</span>
              <h2>Не просто список мест.<br /><em>Личный туристический AI.</em></h2>
            </div>
          </div>

          <div className="feature-grid">
            {features.map((item) => (
              <article className="feature-card" key={item.number}>
                <div className="feature-top">
                  <span className="feature-icon">{item.icon}</span>
                  <span>{item.number}</span>
                </div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section destinations" id="destinations">
          <div className="section-heading compact">
            <div>
              <span className="section-kicker">03 / НАПРАВЛЕНИЯ</span>
              <h2>Россия, которую<br /><em>хочется открыть.</em></h2>
            </div>
            <p>От больших городов до неожиданных мест — ТурГид помогает увидеть Россию по-своему.</p>
          </div>

          <div className="destination-grid">
            {destinations.map(([city, places], index) => (
              <button className={`destination-card destination-${index + 1}`} key={city} onClick={openBot}>
                <span>0{index + 1}</span>
                <div>
                  <h3>{city}</h3>
                  <p>{places}</p>
                </div>
                <b>↗</b>
              </button>
            ))}
          </div>
        </section>

        <section className="max-section">
          <div className="max-copy">
            <span className="section-kicker">04 / ОСНОВНОЙ ПРОДУКТ</span>
            <h2>Весь ТурГид<br /><em>уже внутри MAX.</em></h2>
            <p>
              Сайт рассказывает о проекте, а настоящий маршрут строится
              непосредственно в MAX. Открой бота и попробуй спланировать
              свою следующую поездку.
            </p>
            <button className="primary-btn light" onClick={openBot}>
              Открыть ТурГид в MAX <span>→</span>
            </button>
          </div>

          <div className="qr-card">
            <img src="/qr.svg" alt="QR-код ТурГид Россия в MAX" />
            <strong>Сканируй и запускай</strong>
            <span>ТурГид Россия в MAX</span>
          </div>
        </section>

        <section className="final-cta">
          <div>
            <span className="section-kicker">ГОТОВ?</span>
            <h2>Твоё следующее<br /><em>путешествие уже ждёт.</em></h2>
          </div>
          <button className="primary-btn" onClick={openBot}>
            Спланировать путешествие <span>→</span>
          </button>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-brand">
          <span className="brand-mark">T</span>
          <span>ТурГид <strong>Россия</strong></span>
        </div>
        <span>Умные путешествия по России</span>
        <span>© 2026 ТурГид Россия</span>
      </footer>
    </div>
  );
}

export default App;
