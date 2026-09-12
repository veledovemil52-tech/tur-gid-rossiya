import { useEffect } from "react";
import "./App.css";

const BOT_URL = "https://max.ru/se14052982_bot";

const destinations = [
  {
    city: "Москва",
    meta: "Красная площадь · парки · музеи",
    className: "moscow",
    image: "https://lifeglobe.net/x/entry/16572/1-1771442329553-469659072.jpg",
  },
  {
    city: "Санкт-Петербург",
    meta: "Эрмитаж · Невский · набережные",
    className: "spb",
    image: "https://applescoop.org/image/wallpapers/iphone/vintage-classic-old-winter-palace-saint-petersburg-russia-st-petersburg-soviet-union-style-architecture-01-12-2024-1733101258-hd-wallpaper.jpeg",
  },
  {
    city: "Казань",
    meta: "Кремль · Старо-Татарская слобода",
    className: "kazan",
    image: "https://radotagroup.com/wp-content/uploads/2023/10/200121.jpg",
  },
  {
    city: "Сочи",
    meta: "море · горы · прогулки",
    className: "sochi",
    image: "https://krasnodar.bz/upload/000/u29/2/9/sochi-prinjal-4-5-mln-turistov-s-nachala-2025-goda-photo-content-item.webp",
  },
  {
    city: "Екатеринбург",
    meta: "центр · Урал · современность",
    className: "ekb",
    image: "https://image.produktion.de/1731000.webp?format=jpg&height=720&imageId=1731000&width=960",
  },
  {
    city: "Владивосток",
    meta: "море · мосты · закаты",
    className: "vlad",
    image: "https://news.store.rambler.ru/img/eb259c2aefb4fab4aed1e7b8dff40dd4?img-1-resize=width%3A1280%2Cheight%3A960%2Cfit%3Acover&img-format=auto",
  },
];

const steps = [
  ["01", "⌖", "Выбираешь город", "Любой уголок России — от больших городов до скрытых жемчужин."],
  ["02", "♙", "Рассказываешь о себе", "Интересы, бюджет, компания, количество дней и предпочтения."],
  ["03", "✦", "Получаешь маршрут", "AI собирает план и показывает его в MAX с учётом твоих пожеланий."],
];

const features = [
  ["✦", "AI-маршрут", "Персональный план под твои интересы и темп."],
  ["☁", "Погода", "Адаптируем маршрут под прогноз."],
  ["₽", "Бюджет", "Помогаем спланировать поездку без лишних расходов."],
  ["⌁", "Компания", "Подбираем формат для пары, друзей и семьи."],
  ["⌖", "Карта", "Открывай готовый маршрут и строй путь."],
];

function App() {
  useEffect(() => {
    const elements = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );

    elements.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

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

        <nav className="nav">
          <button onClick={() => scrollTo("how")}>О проекте</button>
          <button onClick={() => scrollTo("features")}>Возможности</button>
          <button onClick={() => scrollTo("destinations")}>Направления</button>
          <button onClick={openBot}>MAX</button>
        </nav>

        <button className="header-cta" onClick={openBot}>
          Открыть в MAX <span>↗</span>
        </button>
      </header>

      <main>
        <section className="hero">
          <div className="hero-bg" aria-hidden="true">
            <div className="hero-mountains back" />
            <div className="hero-mountains front" />
            <div className="hero-lake" />
          </div>
          <div className="hero-glow hero-glow-blue" />
          <div className="hero-glow hero-glow-gold" />

          <div className="hero-copy reveal visible">
            <span className="eyebrow">
              <span className="status-dot" />
              AI-помощник в путешествиях
            </span>

            <h1>
              Путешествия
              <span>начинаются</span>
              <b>здесь.</b>
            </h1>

            <p>
              ТурГид Россия — персональный AI-гид по России.
              Маршрут, который подстраивается под твои интересы,
              бюджет и погоду. Всё это — прямо в MAX.
            </p>

            <div className="hero-actions">
              <button className="primary-btn" onClick={openBot}>
                <span className="max-dot">◉</span>
                Открыть в MAX
                <b>→</b>
              </button>

              <button className="qr-mini" onClick={openBot}>
                <span className="qr-mini-icon">⌗</span>
                <span>
                  <strong>Сканируй QR</strong>
                  <small>и открой бота</small>
                </span>
              </button>
            </div>

            <div className="hero-stats">
              <div><strong>89+</strong><span>городов России</span></div>
              <div><strong>AI</strong><span>персональный маршрут</span></div>
              <div><strong>24/7</strong><span>помощник в поездке</span></div>
            </div>
          </div>

          <div className="hero-phone-wrap reveal visible">
            <div className="hero-phone">
              <div className="phone-top">
                <span>9:41</span><span className="phone-island" /><span>•••</span>
              </div>

              <div className="phone-title">
                <span className="phone-logo">T</span>
                <div><strong>ТурГид Россия</strong><small>Бот</small></div>
              </div>

              <div className="phone-bubble">
                <strong>Привет! 👋</strong>
                <p>Я — ТурГид Россия. Помогу спланировать твоё путешествие по России.</p>
              </div>

              <div className="phone-label">Популярные города</div>
              <div className="phone-cities">
                <span>Москва</span>
                <span>Санкт-Петербург</span>
                <span>Казань</span>
              </div>

              <div className="phone-input">
                <span>Написать сообщение...</span><b>→</b>
              </div>
            </div>

            <div className="hero-qr-card">
              <div className="qr-image-shell">
                <img src="/qr.svg" alt="QR-код ТурГид Россия в MAX" />
              </div>
              <div className="max-word">◉ max</div>
              <p>Сканируй QR<br />и начни путешествие<br />с ТурГид Россия в MAX</p>
            </div>
          </div>
        </section>

        <section className="intro-strip reveal">
          <span>Планируй меньше.</span>
          <strong>Путешествуй больше.</strong>
          <span>Остальное сделает ТурГид.</span>
        </section>

        <section className="how-section" id="how">
          <div className="section-topline reveal">
            <div>
              <h2>Как это работает?</h2>
              <p>Всего 3 шага — и твой маршрут готов.</p>
            </div>
            <div className="hand-note">Твой идеальный<br />маршрут — всего<br />в пару кликов <b>↗</b></div>
          </div>

          <div className="steps">
            {steps.map(([number, icon, title, text], index) => (
              <article className={`step reveal delay-${index + 1}`} key={number}>
                <div className="step-number">{number}</div>
                <div className="step-icon">{icon}</div>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="destinations-section" id="destinations">
          <div className="destination-heading reveal">
            <div>
              <span className="pill-label">НАПРАВЛЕНИЯ</span>
              <h2>Россия, которую<br /><em>хочется открыть.</em></h2>
              <p>От больших городов до живописных природных уголков — выбирай своё направление.</p>
              <button className="dark-btn" onClick={openBot}>Открыть в MAX <span>→</span></button>
            </div>
            <div className="destination-scroll-arrow">→</div>
          </div>

          <div className="destination-list">
            {destinations.map((item, index) => (
              <button
                className={`destination-card reveal delay-${(index % 3) + 1}`}
                key={item.city}
                onClick={openBot}
                style={{ "--city-image": `url("${item.image}")` }}
              >
                <div className="destination-shade" />
                <div className="destination-body">
                  <div className="destination-index">0{index + 1}</div>
                  <div>
                    <h3>{item.city}</h3>
                    <p>{item.meta}</p>
                  </div>
                </div>
                <span className="destination-arrow">↗</span>
              </button>
            ))}
          </div>
        </section>

        <section className="features-section" id="features">
          <div className="feature-intro reveal">
            <span className="pill-label">ВОЗМОЖНОСТИ</span>
            <h2>Больше, чем просто<br /><em>маршрут.</em></h2>
            <p>ТурГид Россия учитывает всё, чтобы твоё путешествие было идеальным.</p>
          </div>

          <div className="feature-list">
            {features.map(([icon, title, text], index) => (
              <article className={`feature reveal delay-${(index % 3) + 1}`} key={title}>
                <div className="feature-top">
                  <span className={`feature-round round-${index}`}>{icon}</span>
                  <span>0{index + 1}</span>
                </div>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}

            <div className="max-card reveal">
              <div>
                <div className="max-card-title"><span className="max-card-logo">◉</span><strong>ТурГид Россия</strong></div>
                <small>уже в MAX</small>
                <button onClick={openBot}>Открыть в MAX →</button>
              </div>
              <div className="max-card-qr"><img src="/qr.svg" alt="QR-код MAX" /></div>
            </div>
          </div>
        </section>

        <section className="max-section reveal">
          <div className="max-copy">
            <span className="pill-label">04 / ОСНОВНОЙ ПРОДУКТ</span>
            <h2>Весь ТурГид<br /><em>уже внутри MAX.</em></h2>
            <p>
              Сайт знакомит с проектом, а настоящая поездка строится внутри MAX —
              от выбора города до готового маршрута, погоды и карты.
            </p>
            <button className="primary-btn light" onClick={openBot}>
              Открыть ТурГид в MAX <b>→</b>
            </button>
          </div>

          <div className="max-phone">
            <div className="max-phone-bar" />
            <div className="max-chat-head">
              <span className="phone-logo dark">T</span>
              <strong>ТурГид Россия</strong>
              <span>•••</span>
            </div>
            <div className="max-chat-message">
              <small>ТурГид AI</small>
              <p>Готово! Я собрал маршрут на 3 дня и учёл прогноз погоды, бюджет и твои интересы.</p>
            </div>
            <div className="max-chat-route">
              <span>⌖</span>
              <div><small>Сегодня</small><strong>Красная площадь → Зарядье</strong></div>
            </div>
            <div className="max-chat-btn">🗺️ Открыть маршрут</div>
          </div>

          <div className="max-section-mountains" />
        </section>

        <section className="final-cta reveal">
          <div>
            <span className="pill-label">ГОТОВ?</span>
            <h2>Твоё следующее<br /><em>путешествие уже ждёт.</em></h2>
          </div>
          <button className="primary-btn" onClick={openBot}>Спланировать путешествие <b>→</b></button>
        </section>
      </main>

      <footer className="footer">
        <div className="footer-brand">
          <span className="brand-mark">T</span>
          <span>ТурГид <strong>Россия</strong></span>
        </div>
        <span>Умные путешествия по России</span>
        <div className="footer-links">
          <button onClick={() => scrollTo("how")}>О проекте</button>
          <button onClick={() => scrollTo("features")}>Возможности</button>
          <button onClick={() => scrollTo("destinations")}>Направления</button>
          <button onClick={openBot}>MAX</button>
        </div>
        <span>© 2026</span>
      </footer>
    </div>
  );
}

export default App;
