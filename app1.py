import streamlit as st
import pandas as pd
from datetime import datetime

# ==============================
# Базови настройки на страницата
# ==============================
st.set_page_config(
    page_title="📊 Класна анкета – Оценяване на хора",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Класна анкета – Оценяване на хора")
st.caption("Малка вътрешна система за оценяване на хора от класа. Не я взимай твърде насериозно 🙂")

# ==============================
# Инициализация на session_state
# ==============================
if "grade_options" not in st.session_state:
    st.session_state.grade_options = ["2", "3", "4", "5", "6"]

if "grades" not in st.session_state:
    st.session_state.grades = {g: 0 for g in st.session_state.grade_options}

# подробен лог: списък от речници
if "records" not in st.session_state:
    st.session_state.records = []  # [{name, grade, timestamp, comment}, ...]

# ==============================
# SIDEBAR – настройки и инфо
# ==============================
with st.sidebar:
    st.header("⚙️ Настройки")

    show_names = st.checkbox("Показвай таблица с хората", value=True)
    show_stats = st.checkbox("Показвай детайлни статистики", value=True)

    st.markdown("—")
    st.subheader("🧹 Нулиране на анкетата")
    if st.button("Изчисти всички данни", type="secondary"):
        st.session_state.grades = {g: 0 for g in st.session_state.grade_options}
        st.session_state.records = []
        st.success("Всички данни бяха изчистени.")

    st.markdown("—")
    st.caption("Tip: можеш да филтрираш и сортираш таблицата по име/оценка от самия интерфейс.")

# ==============================
# Табове: Въвеждане / Анализ
# ==============================
tab_input, tab_results = st.tabs(["✍️ Въвеждане", "📈 Анализ"])

# ==============================
# TAB 1 – Въвеждане
# ==============================
with tab_input:
    st.subheader("Въведи нова оценка")

    with st.form("grade_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])

        with col1:
            name = st.text_input("Име на човек *", placeholder="Пример: Иво")

        with col2:
            grade = st.selectbox(
                "Оценка *",
                st.session_state.grade_options,
                index=st.session_state.grade_options.index("6")
            )

        comment = st.text_area(
            "Коментар (по желание)",
            placeholder="Кратко мнение – защо тази оценка?"
        )

        submitted = st.form_submit_button("💾 Запази оценката")

        if submitted:
            if name.strip() == "":
                st.warning("Моля, въведи име (не може да е празно).")
            else:
                # Ъпдейт на обобщените оценки
                st.session_state.grades[grade] += 1

                # Добавяне към подробния лог
                st.session_state.records.append({
                    "Име": name.strip(),
                    "Оценка": int(grade),
                    "Коментар": comment.strip(),
                    "Време": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                })

                st.success(f"✅ Оценката {grade} за {name.strip()} е записана.")

    st.markdown("---")
    if show_names and len(st.session_state.records) > 0:
        st.subheader("📋 Последно въведени оценки")
        # Показваме последните 10, най-новите отгоре
        df_records = pd.DataFrame(st.session_state.records)
        df_recent = df_records.iloc[::-1].head(10)
        st.dataframe(df_recent, use_container_width=True)

# ==============================
# TAB 2 – Анализ
# ==============================
with tab_results:
    st.subheader("Общо разпределение на оценките")

    grades_df = pd.DataFrame.from_dict(
        st.session_state.grades,
        orient="index",
        columns=["Брой"]
    ).sort_index()

    # Бар диаграма
    st.bar_chart(grades_df)

    # Преобразуваме в по-удобна форма за друг анализ
    grades_df_reset = grades_df.reset_index()
    grades_df_reset.columns = ["Оценка", "Брой"]

    if show_stats:
        st.markdown("---")
        st.subheader("📊 Статистика")

        total_votes = grades_df_reset["Брой"].sum()
        if total_votes == 0:
            st.info("Все още няма въведени оценки.")
        else:
            # Средна оценка (претеглена)
            weighted_sum = (grades_df_reset["Оценка"].astype(int) * grades_df_reset["Брой"]).sum()
            avg_grade = weighted_sum / total_votes

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Общ брой оценки", total_votes)
            with col_b:
                st.metric("Средна оценка", f"{avg_grade:.2f}")
            with col_c:
                best_grade_row = grades_df_reset.loc[grades_df_reset["Брой"].idxmax()]
                st.metric("Най-често срещана оценка", int(best_grade_row["Оценка"]))

            # Пай диаграма – процентно разпределение
            st.markdown("### 🥧 Процентно разпределение")
            pie_df = grades_df_reset.copy()
            pie_df["Процент"] = (pie_df["Брой"] / total_votes * 100).round(1)
            st.dataframe(pie_df, use_container_width=True)

            # Малко текстов анализ
            st.markdown("### 🧠 Кратък анализ")
            if avg_grade >= 5.5:
                st.write("Като цяло сте доста добри един към друг. Средната оценка е почти отлична.")
            elif avg_grade >= 4.5:
                st.write("По-скоро позитивни оценки, но има и критика. Балансирана картинка.")
            elif avg_grade >= 3.5:
                st.write("Малко сте токсик, има повече ниски оценки. Може да сте по-милостиви.")
            else:
                st.write("Тук май се води война. Повечето оценки са ниски – rethink your life choices.")
