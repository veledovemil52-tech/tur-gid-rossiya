import "./App.css";

const BOT_URL = "https://max.ru/se14052982_bot";

const cities = [
  [
    "Москва",
    "Столица в ритме большого города",
    "https://images.unsplash.com/photo-1513326738677-b964603b136d?auto=format&fit=crop&w=1200&q=88",
  ],
  [
    "Санкт-Петербург",
    "Архитектура, история и атмосфера Невы",
    "https://images.unsplash.com/photo-1556610961-2fecc5927173?auto=format&fit=crop&w=1200&q=88",
  ],
  [
    "Казань",
    "Кремль, мечеть Кул-Шариф и восточный характер",
    "https://commons.wikimedia.org/wiki/Special:FilePath/Qol%C5%9F%C3%A4rif%20Mosque%20in%20Kazan%2C%20Russia.jpg",
  ],
  [
    "Сочи",
    "Море, пляж и вечерний курортный город",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=88",
  ],
];

const features = [
  [
    "01",
    "✦",
    "AI-маршрут",
    "Персональная программа под твои интересы, компанию и бюджет.",
  ],
  [
    "02",
    "☼",
    "Погода",
    "Маршрут меняется под прогноз, чтобы плохая погода не сломала день.",
  ],
  [
    "03",
    "₽",
    "Бюджет",
    "Укажи сумму на поездку — ТурГид учитывает её при составлении маршрута.",
  ],
  [
    "04",
    "⌖",
    "Карта",
    "Готовый маршрут можно открыть на карте и сразу отправиться в путь.",
  ],
];

const botScreens = [
  [
    "01",
    "Выбор города",
    "Найди город и начни настройку поездки",
    "/bot-1.png",
  ],
  [
    "02",
    "Дни и бюджет",
    "Задай длительность и сумму поездки",
    "/bot-2.png",
  ],
  [
    "03",
    "Интересы",
    "Выбери то, что действительно нравится",
    "/bot-3.png",
  ],
  [
    "04",
    "Готовый маршрут",
    "Получи маршрут и открой его на карте",
    "/bot-4.png",
  ],
];

function App() {
  return (
    <div className="site">

      {/* HEADER */}
      <header className="header">
        <div className="header-inner">

          <a href="#top" className="brand">
            <span className="brand-mark">T</span>

            <span>
              <strong>ТурГид</strong>
              <small>РОССИЯ</small>
            </span>
          </a>

          <nav>
            <a href="#how">Как работает</a>
            <a href="#features">Возможности</a>
            <a href="#destinations">Направления</a>
            <a href="#bot">MAX</a>
          </nav>

          <a
            className="header-button"
            href={BOT_URL}
            target="_blank"
            rel="noreferrer"
          >
            Открыть в MAX ↗
          </a>

        </div>
      </header>

      <main id="top">

        {/* HERO */}
        <section className="hero">

          <div className="hero-copy">

            <div className="eyebrow">
              <i />
              УМНЫЙ AI-ГИД ПО РОССИИ
            </div>

            <h1>
              Путешествия
              <em>начинаются</em>
              здесь.
            </h1>

            <p>
              ТурГид Россия создаёт персональные маршруты по городам России
              с учётом твоих интересов, бюджета, компании и погоды.
            </p>

            <div className="hero-actions">

              <a
                className="primary-button"
                href={BOT_URL}
                target="_blank"
                rel="noreferrer"
              >
                Спланировать путешествие
                <b>→</b>
              </a>

              <a className="secondary-button" href="#how">
                Как это работает
              </a>

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

            <div className="hero-photo">

              <span className="hero-photo-title">
                Путешествие
                <br />
                по России
              </span>

              <span className="hero-photo-caption">
                Россия —
                <em>это близко.</em>
              </span>

            </div>

            <div className="hero-chip weather">
              <span>☀️</span>
              <b>+18°</b>
              <small>погода учтена</small>
            </div>

            <div className="hero-chip route">
              <span>✦</span>

              <div>
                <small>AI-МАРШРУТ</small>
                <b>Маршрут готов</b>
              </div>
            </div>

          </div>

        </section>

        {/* HOW IT WORKS */}
        <section className="how dark" id="how">

          <div className="wrap">

            <div className="how-head">

              <div>

                <div className="eyebrow light">
                  <i />
                  КАК ЭТО РАБОТАЕТ
                </div>

                <h2>
                  Три шага до
                  <br />
                  <em>готового маршрута.</em>
                </h2>

              </div>

              <p>
                Простой диалог внутри MAX:
                город → параметры поездки → готовый маршрут.
              </p>

            </div>

            <div className="steps">

              <article>
                <small>01</small>

                <span>⌖</span>

                <h3>Выбери город</h3>

                <p>
                  Москва, Петербург, Казань,
                  Сочи или любой другой город России.
                </p>
              </article>

              <article>
                <small>02</small>

                <span>◌</span>

                <h3>Расскажи о поездке</h3>

                <p>
                  Компания, количество дней,
                  бюджет и интересы.
                </p>
              </article>

              <article>
                <small>03</small>

                <span>✦</span>

                <h3>Получи маршрут</h3>

                <p>
                  AI соберёт программу по дням
                  с учётом погоды и твоих пожеланий.
                </p>
              </article>

            </div>

          </div>

        </section>

        {/* FEATURES */}
        <section className="features" id="features">

          <div className="wrap">

            <div className="section-head">

              <div>

                <div className="eyebrow">
                  <i />
                  ВОЗМОЖНОСТИ
                </div>

                <h2>
                  Не просто гид.
                  <br />
                  <em>Твой персональный</em>
                  <br />
                  помощник.
                </h2>

              </div>

              <p>
                ТурГид учитывает интересы,
                бюджет и погоду и собирает
                поездку в одном месте.
              </p>

            </div>

            <div className="feature-grid">

              {features.map(([number, icon, title, text]) => (

                <article className="feature" key={number}>

                  <div className="feature-top">

                    <span>{icon}</span>

                    <small>{number}</small>

                  </div>

                  <div>

                    <h3>{title}</h3>

                    <p>{text}</p>

                  </div>

                  <b>↗</b>

                </article>

              ))}

            </div>

          </div>

        </section>

        {/* DESTINATIONS */}
        <section className="destinations dark" id="destinations">

          <div className="wrap">

            <div className="section-head dest-head">

              <div>

                <div className="eyebrow light">
                  <i />
                  НАПРАВЛЕНИЯ
                </div>

                <h2>
                  Куда отправимся
                  <br />
                  <em>сегодня?</em>
                </h2>

              </div>

              <p>
                Выбирай город —
                маршрут соберёт ТурГид внутри MAX.
              </p>

            </div>

            <div className="city-grid">

              {cities.map(([name, subtitle, image], index) => (

                <a
                  className="city"
                  href={BOT_URL}
                  target="_blank"
                  rel="noreferrer"
                  key={name}
                >

                  <img
                    src={image}
                    alt={name}
                  />

                  <div className="city-overlay" />

                  <small>
                    0{index + 1}
                  </small>

                  <div>

                    <h3>{name}</h3>

                    <p>{subtitle}</p>

                  </div>

                  <b>↗</b>

                </a>

              ))}

            </div>

          </div>

        </section>

        {/* REAL BOT */}
        <section className="bot" id="bot">

          <div className="wrap">

            <div className="section-head bot-head">

              <div>

                <div className="eyebrow">
                  <i />
                  РЕАЛЬНЫЙ БОТ
                </div>

                <h2>
                  Как ТурГид
                  <br />
                  <em>выглядит в MAX.</em>
                </h2>

              </div>

              <p>
                Настоящие экраны работающего проекта —
                от выбора города до готового маршрута.
              </p>

            </div>

            <div className="screens">

              {botScreens.map(
                ([number, title, text, image]) => (

                  <article
                    className="screen-card"
                    key={image}
                  >

                    <div className="screen-image">

                      <img
                        src={image}
                        alt={title}
                      />

                    </div>

                    <small>{number}</small>

                    <h3>{title}</h3>

                    <p>{text}</p>

                  </article>

                )
              )}

            </div>

            <div className="bot-cta">

              <div>

                <small>
                  ТУРГИД РОССИЯ × MAX
                </small>

                <h3>
                  Попробуй сам.
                </h3>

              </div>

              <a
                className="primary-button"
                href={BOT_URL}
                target="_blank"
                rel="noreferrer"
              >
                Открыть бота в MAX
                <b>↗</b>
              </a>

            </div>

          </div>

        </section>

        {/* FINAL */}
        <section className="final">

          <div>

            <div className="eyebrow light">
              <i />
              ГОТОВ?
            </div>

            <h2>
              Россия ближе,
              <br />
              <em>чем кажется.</em>
            </h2>

            <p>
              Выбери город. Расскажи о своих планах.
              Остальное сделает ТурГид.
            </p>

            <a
              className="primary-button"
              href={BOT_URL}
              target="_blank"
              rel="noreferrer"
            >
              Спланировать путешествие
              <b>→</b>
            </a>

          </div>

        </section>

      </main>

      {/* FOOTER */}
      <footer>

        <div className="footer-inner">

          <a href="#top" className="brand">

            <span className="brand-mark">
              T
            </span>

            <span>
              <strong>ТурГид</strong>
              <small>РОССИЯ</small>
            </span>

          </a>

          <span>
            Умные путешествия по России
          </span>

          <a
            href={BOT_URL}
            target="_blank"
            rel="noreferrer"
          >
            MAX ↗
          </a>

          <span>
            © 2026
          </span>

        </div>

      </footer>

    </div>
  );
}

export default App;