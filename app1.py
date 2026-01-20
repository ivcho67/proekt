import streamlit as st
import pandas as pd
from datetime import datetime

# Базови настройки на страницата
st.set_page_config(
    page_title="🎬 Филмов Критик – Оценяване на заглавия",
    page_icon="🍿",
    layout="centered"
)

st.title("🎬 Филмов Критик – Твоето мнение")
st.caption("Система за събиране на оценки и ревюта за гледани филми.")

# Инициализация на session_state
if "star_options" not in st.session_state:
    st.session_state.star_options = ["1 ⭐", "2 ⭐", "3 ⭐", "4 ⭐", "5 ⭐"]

if "rating_counts" not in st.session_state:
    st.session_state.rating_counts = {s: 0 for s in st.session_state.star_options}

if "movie_logs" not in st.session_state:
    st.session_state.movie_logs = [] 

# SIDEBAR – настройки
with st.sidebar:
    st.header("⚙️ Контролен панел")
    show_history = st.checkbox("Покажи история на ревютата", value=True)
    show_analytics = st.checkbox("Покажи детайлен анализ", value=True)

    st.markdown("---")
    if st.button("Изтрий всички ревюта", type="primary"):
        st.session_state.rating_counts = {s: 0 for s in st.session_state.star_options}
        st.session_state.movie_logs = []
        st.success("Базата данни е нулирана.")

# Табове
tab_vote, tab_stats = st.tabs(["🎥 Добави Ревю", "📊 Статистика на филмите"])

# TAB 1 – Въвеждане на филм
with tab_vote:
    st.subheader("Оцени филм")

    with st.form("movie_form", clear_on_submit=True):
        m_name = st.text_input("Заглавие на филм *")
        
        col_gen, col_rat = st.columns(2)
        with col_gen:
            genre = st.selectbox("Жанр", ["Екшън", "Комедия", "Драма", "Фантастика", "Ужаси"])
        with col_rat:
            rating = st.selectbox("Оценка *", st.session_state.star_options, index=4)

        review = st.text_area("Кратко ревю")
        submitted = st.form_submit_button("🚀 Публикувай ревю")

        if submitted:
            if m_name.strip() == "":
                st.error("Моля, въведете заглавие на филма!")
            else:
                # Обновяване на брояча
                st.session_state.rating_counts[rating] += 1
                
                # Добавяне в лога
                st.session_state.movie_logs.append({
                    "Филм": m_name.strip(),
                    "Жанр": genre,
                    "Рейтинг": rating,
                    "Коментар": review.strip(),
                    "Дата": datetime.now().strftime("%H:%M - %d.%m.%y")
                })
                st.balloons()
                st.success(f"Ревюто за '{m_name}' е добавено успешно!")

    if show_history and len(st.session_state.movie_logs) > 0:
        st.markdown("---")
        st.subheader("📜 Последни ревюта")
        df_movies = pd.DataFrame(st.session_state.movie_logs)
        st.table(df_movies.iloc[::-1].head(5))

# TAB 2 – Анализ на данните
with tab_stats:
    st.subheader("Разпределение на звездите")
    
    # Подготовка на данни за графика
    stats_df = pd.DataFrame.from_dict(
        st.session_state.rating_counts, 
        orient="index", 
        columns=["Брой гласове"]
    )
    st.bar_chart(stats_df)

    if show_analytics:
        st.markdown("---")
        total_reviews = sum(st.session_state.rating_counts.values())
        
        if total_reviews > 0:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Общо ревюта", total_reviews)
            with c2:
                # Намиране на най-популярната оценка
                popular_rating = max(st.session_state.rating_counts, key=st.session_state.rating_counts.get)
                st.metric("Най-честа оценка", popular_rating)
            
            st.markdown("### Подробен отчет")
            report_df = stats_df.copy().reset_index()
            report_df.columns = ["Рейтинг", "Брой"]
            st.dataframe(report_df, use_container_width=True)
        else:
            st.info("Няма данни за анализ. Добавете първото си ревю!")
